```shell
curl -X POST http://127.0.0.1:5000/add_sign_image \
-F "pdf_path=/absolute/path/to/your.pdf" \
-F "page_number=1" \
-F "data=Sample QR Code Data" \
-F "x=100" \
-F "y=200" \
-F "w=150" \
-F "h=150"
```