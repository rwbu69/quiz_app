from app import app
from database.models import db, Question


def seed_questions():
    with app.app_context():
        questions = [
            Question(
                question_text="Apa kepanjangan dari NLP dalam ilmu komputer?",
                option1="Natural Language Processing",
                option2="Neural Language Program",
                option3="National Language Protocol",
                option4="Network Learning Process",
                correct_option=1,
                category="NLP Basics",
                difficulty=1,
            ),
            Question(
                question_text="Apa tujuan utama dari Natural Language Processing?",
                option1="Membuat komputer memahami bahasa manusia",
                option2="Menerjemahkan bahasa pemrograman",
                option3="Meningkatkan kecepatan komputer",
                option4="Menyimpan data bahasa",
                correct_option=1,
                category="NLP Basics",
                difficulty=1,
            ),
            Question(
                question_text="Apa yang dimaksud dengan tokenisasi dalam NLP?",
                option1="Memecah teks menjadi kata-kata atau frasa",
                option2="Menerjemahkan bahasa",
                option3="Menyimpan dokumen teks",
                option4="Mengenkripsi pesan",
                correct_option=1,
                category="NLP Techniques",
                difficulty=2,
            ),
            Question(
                question_text="Apa contoh aplikasi NLP dalam kehidupan sehari-hari?",
                option1="Asisten virtual seperti Siri atau Google Assistant",
                option2="Software pengolah gambar",
                option3="Aplikasi kalkulator",
                option4="Program spreadsheet",
                correct_option=1,
                category="NLP Applications",
                difficulty=1,
            ),
            Question(
                question_text="Apa yang dilakukan oleh stemming dalam NLP?",
                option1="Mengurangi kata ke bentuk dasarnya",
                option2="Menerjemahkan antar bahasa",
                option3="Mengidentifikasi nama orang",
                option4="Menganalisis sentiment",
                correct_option=1,
                category="NLP Techniques",
                difficulty=2,
            ),
            Question(
                question_text="Apa itu stop words dalam NLP?",
                option1="Kata umum yang sering diabaikan (contoh: dan, di, yang)",
                option2="Kata-kata penting dalam dokumen",
                option3="Kata terakhir dalam kalimat",
                option4="Kata yang salah eja",
                correct_option=1,
                category="NLP Concepts",
                difficulty=1,
            ),
            Question(
                question_text="Apa yang dimaksud dengan sentiment analysis?",
                option1="Mengidentifikasi emosi dalam teks",
                option2="Memeriksa tata bahasa",
                option3="Menerjemahkan bahasa",
                option4="Menyimpan dokumen teks",
                correct_option=1,
                category="NLP Applications",
                difficulty=2,
            ),
            Question(
                question_text="Apa itu word embedding dalam NLP?",
                option1="Representasi numerik dari kata-kata",
                option2="Jumlah kata dalam dokumen",
                option3="Cara menyimpan dokumen",
                option4="Teknik pencetakan kata",
                correct_option=1,
                category="NLP Concepts",
                difficulty=3,
            ),
            Question(
                question_text="Manakah yang BUKAN termasuk library NLP?",
                option1="TensorFlow Graphics",
                option2="NLTK",
                option3="spaCy",
                option4="Hugging Face Transformers",
                correct_option=1,
                category="NLP Tools",
                difficulty=2,
            ),
            Question(
                question_text="Apa yang dimaksud dengan POS tagging?",
                option1="Memberi label kategori gramatikal pada kata",
                option2="Menentukan lokasi geografis dari teks",
                option3="Mengurutkan kata berdasarkan abjad",
                option4="Menghitung jumlah kata",
                correct_option=1,
                category="NLP Techniques",
                difficulty=2,
            ),
        ]

        Question.query.delete()

        db.session.bulk_save_objects(questions)
        db.session.commit()
        print(f"Berhasil menambahkan {len(questions)} pertanyaan NLP!")


if __name__ == "__main__":
    seed_questions()
