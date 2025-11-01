from flask import Flask, render_template, request, jsonify
import psycopg2
import google.generativeai as genai
import os

app = Flask(__name__)

# --- Cấu hình ---
genai.configure(api_key=os.environ.get("GEMINI_API"))

# Kết nối đến Cloud PostgreSQL
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.get_json().get("question", "")
    cur = conn.cursor()

    # Lấy tất cả phim từ DB (có thể tối ưu sau)
    cur.execute("SELECT name, genre, director, actors, release_year, language, content FROM movies2;")
    movies = cur.fetchall()
    cur.close()

    # Ghép dữ liệu phim thành ngữ cảnh
    movie_info = "\n".join(
        [f"Tên: {m[0]}, Thể loại: {m[1]}, Đạo diễn: {m[2]}, Diễn viên: {m[3]}, Năm: {m[4]}, Ngôn ngữ: {m[5]}, Mô tả: {m[6]}"
         for m in movies[:50]]  # tránh gửi quá nhiều
    )

    prompt = f"""
    Bạn là chatbot chuyên về phim. Dưới đây là danh sách phim bạn có trong cơ sở dữ liệu:

    {movie_info}

    Câu hỏi của người dùng: "{question}"

    Dựa trên dữ liệu trên, hãy trả lời ngắn gọn, tự nhiên và chính xác.
    Nếu không có thông tin, hãy nói rằng bạn không tìm thấy phim phù hợp.
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    answer = response.text.strip()

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
