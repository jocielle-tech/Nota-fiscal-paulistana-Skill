# Prévia municipal e teste explícito do layout 2

Este fluxo adicional prepara RPS municipal de São Paulo com os schemas v02-5. Não substitui automaticamente os emissores existentes e não habilita produção. A integração com os fluxos legados deve ser revisada antes de adoção.

`previsualizar_nfse_municipal.py` valida localmente, sem rede, certificado, senha, assinatura ou avanço de contador:

```bash
python previsualizar_nfse_municipal.py --config config-preview.exemplo.json --dados payload-layout2-municipal.exemplo.json
python -m unittest discover -s tests -v
```

Config e payload de exemplo são fictícios, para validação estrutural. Códigos e retenções devem ser escolhidos para cada operação com o responsável fiscal; os valores do exemplo não são padrões universais.

O total deve ser informado explicitamente em `valor_final_cobrado`, positivo. Valor inicial e conversão implícita do antigo `valor_servicos` são rejeitados. `cIndOp` preserva seis dígitos. `indDest=1` exige destinatário explícito. Local de prestação nacional e país estrangeiro são escolhas exclusivas. Os indicadores `indFinal`, `finNFSe` e `ExigibilidadeSuspensa` permanecem no XML. No perfil implementado, `gTribRegular` é omitido para 200029 e exigido para classificação com prefixo 550; outros perfis requerem revisão.

`schemas/preview` omite apenas as duas assinaturas obrigatórias. Validação de prévia não comprova autorização ou assinatura. `schemas/official` conserva os XSD oficiais completos.

`testar_nfse_municipal.py` também faz apenas prévia por padrão. `--enviar-teste` acessa certificado e senha locais e solicita exclusivamente `TesteEnvioLoteRPS`: usar somente após autorização explícita para teste remoto e com dados revisados. Endpoint/action são fixos, sem redirects, proxies de ambiente ou reenvio automático. Não há emissão, cancelamento ou alteração do contador nesse cliente. HTTP 200 sozinho não aprova o teste: exige confirmação municipal sem erros. O módulo `fiscal_safety.py` protege somente os novos fluxos que o invocam; não bloqueia os scripts legados.

Limites: não implementa numeração/idempotência de produção nem assinatura com intermediário. A validação local rejeita tomador igual ao prestador. Não certifica adequação tributária nem todos os perfis municipais.

Fontes: [manual municipal 3.3.9](https://notadomilhao.sf.prefeitura.sp.gov.br/wp-content/uploads/2026/10/NFe_Web_Service-v3.3.9.pdf), [schemas v02-5](https://notadomilhao.sf.prefeitura.sp.gov.br/schemas-reformatributaria-v02-5).
