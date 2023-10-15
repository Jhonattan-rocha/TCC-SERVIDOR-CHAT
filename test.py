import requests

request = requests.get('https://www.youtube.com/watch?v=oLUx_tAIrBk&list=RDoLUx_tAIrBk&start_radio=1',
                       headers={'Content-Type': 'application/json'})


with open('./Teste.html', 'wb') as file:
    file.write(request.content)

# from requests_toolbelt import MultipartEncoder
#
# mime = MimeTypes()
# nome = "test.png"
# mimetype = mime.guess_type(nome)
# multipart = MultipartEncoder(fields={
#     "originalname": nome,
#     "filename": nome,
#     "id_dono": "4",
#     "id_empresa_dona": "5",
#     "mime_type": mimetype[0],
#     "id_chamado": "2",
#     "file": (nome, open(nome, 'rb'), mimetype[0])
# })
#
# url = "http://10.0.0.103:3001/"
#
# token = requests.post(url + "token/", headers={"Authorization": "application/json"},
#                       data={"email": "jhonattan4rocha@gmail.com", "password": "123", "type": "fu"})
#
# headers = {
#     "Authorization": "Bearer "+token.json()['token'],
#     "Content-Type": multipart.content_type
# }
#
# request = requests.post(url+"arquivo/", headers=headers, data=multipart)
#
# print(request.text)
