"""Fiscal maintenance lock and unsigned, network-free local validation.

No runtime flag, environment variable or config value enables fiscal writes.
Re-enabling operations requires a separate reviewed code change.
"""
import json
from pathlib import Path
from datetime import date
from decimal import Decimal, InvalidOperation

BASE_DIR = Path(__file__).resolve().parent

class FiscalOperationBlocked(RuntimeError):
    pass


def blocked_result(operation):
    return {'sucesso': False, 'bloqueado': True, 'operacao': operation,
            'rede_utilizada': False, 'assinatura_realizada': False,
            'contador_alterado': False, 'emissao_realizada': False,
            'cancelamento_realizado': False,
            'erros': [{'codigo': 'MAINTENANCE_LOCK',
                       'descricao': 'Operação fiscal bloqueada em manutenção. Use --dry-run apenas para validação local não assinada.'}]}


def _read_object(filename):
    path = Path(filename)
    if not path.is_absolute():
        path = BASE_DIR / path
    with path.open('r', encoding='utf-8') as file:
        value = json.load(file)
    if not isinstance(value, dict):
        raise ValueError('O arquivo deve conter um objeto JSON.')
    return value


def _preview_result(operation, errors, **metadata):
    return {'sucesso': not errors, 'dry_run': True,
            'tipo': 'validacao_local_nao_assinada', 'operacao': operation,
            'bloqueio_fiscal_ativo': True, 'rede_utilizada': False,
            'assinatura_realizada': False, 'contador_alterado': False,
            'emissao_realizada': False, 'cancelamento_realizado': False,
            'erros': errors,
            'limitacoes': ['Não valida regras tributárias, assinaturas ou aceitação pelo serviço fiscal.',
                          'Não gera documento fiscal nem XML assinado; XML de prévia é apenas rascunho.'], **metadata}


def preview_emission(config_file, data_file, mode, layout):
    errors = []
    if layout not in (1, 2) or mode not in ('teste', 'producao'):
        return _preview_result('emissao', [{'codigo': 'ARGUMENT', 'descricao': 'Layout ou modo inválido.'}])
    try:
        config = _read_object(config_file)
        data = _read_object(data_file)
    except (OSError, ValueError) as error:
        return _preview_result('emissao', [{'codigo': 'LOCAL_INPUT', 'descricao': type(error).__name__}])
    if layout == 2:
        from municipal_layout2 import municipal_preview
        try:
            metadata = municipal_preview(config, data)
        except (ValueError, KeyError, TypeError, OverflowError) as error:
            return _preview_result('emissao', [{'codigo':getattr(error,'code','MUNICIPAL_PAYLOAD'),'descricao':str(error),'origem':'validacao_local'}], layout=2, modo=mode)
        return _preview_result('emissao', [], layout=2, modo=mode, **metadata)
    required = ['data_emissao', 'valor_servicos', 'documento_tomador', 'discriminacao']
    required += ['numero_rps'] if layout == 1 else ['numero_dps', 'codigo_nbs', 'cClassTrib', 'cIndOp', 'cLocalidadeIncid']
    missing = [key for key in required if data.get(key) in (None, '')]
    missing_config = [key for key in ('cnpj_prestador', 'inscricao_municipal') if not config.get(key)]
    if missing or missing_config:
        errors.append({'codigo': 'PAYLOAD', 'descricao': 'Campos obrigatórios ausentes.',
                       'campos_dados': missing, 'campos_config': missing_config})
    try:
        amount = Decimal(str(data.get('valor_servicos')))
        if not amount.is_finite() or amount <= 0:
            raise ValueError('Valor inválido.')
    except (InvalidOperation, ValueError):
        errors.append({'codigo': 'VALUE', 'descricao': 'valor_servicos deve ser positivo e finito.'})
    try:
        date.fromisoformat(str(data.get('data_emissao')))
    except ValueError:
        errors.append({'codigo': 'DATE', 'descricao': 'data_emissao deve ser uma data ISO válida.'})
    number = str(data.get('numero_rps' if layout == 1 else 'numero_dps', ''))
    if not number.isascii() or not number.isdigit() or int(number or '0') <= 0:
        errors.append({'codigo': 'NUMBER', 'descricao': 'Informar número positivo explicitamente; a validação não reserva ou avança sequência.'})
    return _preview_result('emissao', errors, layout=layout, modo=mode,
                           campos_presentes=sorted(data))


def preview_cancellation(number, config_file='config.json'):
    errors = []
    text = str(number).strip()
    if not text.isascii() or not text.isdigit() or int(text or '0') <= 0:
        errors.append({'codigo': 'NUMBER', 'descricao': 'Informar número de nota positivo.'})
    try:
        config = _read_object(config_file)
        if not config.get('cnpj_prestador') or not config.get('inscricao_municipal'):
            errors.append({'codigo': 'CONFIG', 'descricao': 'Prestador ausente na configuração.'})
    except (OSError, ValueError) as error:
        errors.append({'codigo': 'LOCAL_INPUT', 'descricao': type(error).__name__})
    return _preview_result('cancelamento', errors)
