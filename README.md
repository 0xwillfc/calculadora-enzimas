# Calculadora de Atividade Enzimática

Aplicação desktop em Python/Tkinter para cálculo de atividade enzimática de CAT, GST e SOD.

## Arquivos

- `gui_calculadora.py`: versão inicial da interface.
- `gui_calculadora_completa.py`: versão expandida, com suporte a CAT, GST e dois métodos para SOD.

## Melhorias aplicadas na versão completa

- validação explícita de entrada com mensagens por campo;
- suporte consistente a vírgula decimal;
- remoção de repetição entre CAT e GST por meio de configuração orientada ao ensaio;
- separação mais clara entre regras de cálculo e montagem da interface;
- nomes e constantes alinhados ao domínio experimental.

## Execução

```powershell
python gui_calculadora_completa.py
```

## Histórico

O repositório foi organizado para preservar duas etapas do desenvolvimento:

- `2025-07-02`: versão inicial;
- `2025-07-04`: versão completa.
