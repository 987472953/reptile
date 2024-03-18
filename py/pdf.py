
from urllib.parse import urlencode, quote

a = 'couple-im-api/src/main/java/com/qufaya/im/api/controller/dto/ImConfigDTO.java'
encoded_a = quote(a)
print(encoded_a)