# Projeto de Processamento Digital de Imagens (PDI) - 2019.2
## Universidade Federal do Ceará - UFC

Este projeto consiste em um gerador de vídeo com o objetivo de simular parte do processo de fabricação de torradas. Ele será utilizado como base para o restante do projeto de PDI que consiste em identificar, por meio de processamento digital de imagens, as torradas que não estão devidamente alinhadas para o empacotamento.

### Utilização do sistema

O vídeo é gerado com base em alguns parametros que se encontram no ínicio do arquivo [video_generator.py](https://github.com/matheus220/projeto_pdi/blob/48cc74c7a7e53c845b9086fcc897583b8dfa0824/scripts/video_generator.py#L11-L46) em uma seção nomeada de **SYSTEM PARAMETERS**. Antes de executar o código é importante alterar os parametros para os desejados.

Em seguida é necessário apenas lançar o arquivo python [video_generator.py](https://github.com/matheus220/projeto_pdi/blob/48cc74c7a7e53c845b9086fcc897583b8dfa0824/scripts/video_generator.py). Para isso, basta executar o comando abaixo a partir da pasta **scripts**.

```sh
python video_generator.py
```

> Como resultado serão gerados um vídeo no formato .avi e um arquivo .txt contendo o conjunto de parametros utilizados na criação do vídeo. Ambos estarão em uma pasta chamada **results** localizada na raiz do projeto.
