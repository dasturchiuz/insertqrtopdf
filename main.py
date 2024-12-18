from flask import Flask, jsonify, request, send_file
import fitz
import os
import qrcode

app = Flask(__name__)

@app.route('/add_sign_image', methods=['POST'])
def add_sign_image():
    scaled_size = 1.5
    try:
         # Absalute path bo'ladi
        pdf_path = request.form.get('pdf_path')
        # PDF fayli mavjudligini tekshirish
        if not pdf_path:
            return jsonify({"error": "Missing 'pdf_path' parameter"}), 400
        pdf_path = os.path.abspath(pdf_path)
        # PDF fayli mavjudligini tekshirish
        if not os.path.exists(pdf_path):
            return jsonify({"error": f"PDF not found at path: {pdf_path}"}), 404

        # Formdan ma'lumotlarni olish
        try:        
            page_number = int(request.form.get('page_number'))
            qr_data = request.form.get('data', 'Default QR Code Data')

            x= float(request.form.get('x', 50))
            y= float(request.form.get('y', 50))
            w=float(request.form.get('w', 50))
            h=float(request.form.get('h', 50))
        except ValueError as e:
            return jsonify({"error": f"Parametr qiymati yaroqsiz: {str(e)}"}), 400
        
        # Mashshtab asosida koordinatalarni sozlaymiz
        x= x / scaled_size
        y= y / scaled_size
        # Pdf faylini ochishni tekshirish
        try:
            pdf_document = fitz.open(pdf_path)
        except Exception as e:
            return jsonify({"error": f"PDF faylini ochib bo'lmadi: {str(e)}"}), 500

        # Sahifa raqamlarini tekshirish
        if page_number < 1 or page_number > len(pdf_document):
            pdf_document.close()
            return jsonify({"error": f"Invalid page number: {page_number}"}), 400
        
        page = pdf_document[page_number - 1]
        # QR kodni yaratish
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=20,
                border=0,
            )

            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            # Save QR code as an image
            qr_image_path = 'temp_qr.png'
            qr_img.save(qr_image_path)
        except Exception as e:
            pdf_document.close()
            return jsonify({"error": f"Failed to generate QR code: {str(e)}"}), 500
        
        # QR kodni sahifaga qo'shish
        try:
            image_rect = fitz.Rect(x, y, x + w, y + h)
            page.insert_image(image_rect, filename=qr_image_path)
        except Exception as e:
            pdf_document.close()
            return jsonify({"error": f"Failed to insert image into PDF: {str(e)}"}), 500
        
        # PDF faylni saqlash
        try:
            # Save the modified PDF
            pdf_document.save("pdf_path.pdf")
        except Exception as e:
            pdf_document.close()
            return jsonify({"error": f"Failed to save PDF: {str(e)}"}), 500
        # PDF faylni yopish
        pdf_document.close()
        # QR kodni o'chirish
        os.remove(qr_image_path)
        # Natijani qaytarish
        return jsonify({"message": "QR code added successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": f"Kutilmagan xatolik yuz berdi: {str(e)}"}), 500

   
if __name__ == '__main__':
    app.run(debug=True)

