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

## Testes de regressão

São 33 testes locais, sem serviço fiscal ou certificado real. Além do payload e dos schemas, cobrem assinatura RSA-SHA1 e verificação XML com chaves efêmeras, transporte simulado sem reenvio, funcionamento das CLIs fora da pasta da skill e JSON UTF-8 no Windows. A prévia rejeita intermediários ainda não implementados antes de acessar credenciais.

O parser exige Envelope/Body SOAP, TesteEnvioLoteRPSResponse, RetornoXML único e raiz municipal RetornoEnvioLoteRPS. Rejeita respostas de outro método, SOAP Fault, confirmação ambígua e erros municipais. Preserva alertas longos sem convertê-los em erro: há retornos municipais cujo texto excede o limite do XSD arquivado. Essa verificação de protocolo não é uma validação integral do schema de resposta.

Foi concluído separadamente um ciclo autorizado de emissão e cancelamento reais usando o construtor municipal, com consultas independentes. Esse executor controlado não faz parte do PR e não demonstra homologação da integração com os emissores legados. Divergências entre os retornos de consulta e os XSD arquivados permanecem uma pendência desse fluxo separado. Não adicionar respostas reais, documentos fiscais ou dados pessoais aos testes públicos.

Fontes: [manual municipal 3.3.9](https://notadomilhao.sf.prefeitura.sp.gov.br/wp-content/uploads/2026/10/NFe_Web_Service-v3.3.9.pdf), [schemas v02-5](https://notadomilhao.sf.prefeitura.sp.gov.br/schemas-reformatributaria-v02-5).
