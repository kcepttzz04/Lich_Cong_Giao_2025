import requests
import telebot
import os
import sys
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ForceReply

# Cấu hình Bot
API_TOKEN_BOT = "8168755374:AAH_pQrXdvgG_3rzjw8Rq72o9QbH-her_gY"
bot = telebot.TeleBot(API_TOKEN_BOT)
BOT_B_TOKEN = "7867676996:AAEVZQaR6aQZBq2h-4w7JzcBP-BSgXKLPVQ"
CHAT_ID_B = "-4712065072"

# Số tài khoản và ngân hàng
STK = "359577004"
BANK = "VIB"

# Hàm tạo liên kết QR
def qrlink(STK, BANK, so_tien, noi_dung, download):
    qrlink = f"https://qr.sepay.vn/img?acc={STK}&bank={BANK}&amount={so_tien}&des={noi_dung}&template=compact&download={download}"
    return qrlink

# Xử lý lệnh /start
@bot.message_handler(commands=["start"])
def start(message):
    markup = InlineKeyboardMarkup()
    donate = InlineKeyboardButton("zzDonate meee<333zz", callback_data="donate")  # Sửa: xóa types.
    markup.row(donate)
    bot.send_message(
        message.chat.id,
        "<b>Chào mừng bạn đến với tool của chúng tôi!</b>",  # Hoàn thiện tin nhắn
        parse_mode="HTML",
        reply_markup=markup
    )

# Xử lý nút "Donate"
@bot.callback_query_handler(func=lambda call: call.data == "donate")
def donate(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    markup = InlineKeyboardMarkup()
    t1 = InlineKeyboardButton("10.000", callback_data="10k")  # Sửa: xóa types.
    t2 = InlineKeyboardButton("20.000", callback_data="20k")  # Sửa: xóa types.
    t3 = InlineKeyboardButton("50.000", callback_data="50k")  # Sửa: xóa types.
    t4 = InlineKeyboardButton("100.000", callback_data="100k")  # Sửa: thay - thành =
    t5 = InlineKeyboardButton("200.000", callback_data="200k")  # Sửa: xóa types.
    t6 = InlineKeyboardButton("500.000", callback_data="500k")  # Sửa: xóa types.
    t7 = InlineKeyboardButton("Số Khác", callback_data="khac")  # Sửa: xóa types.
    markup.row(t1, t2, t3)
    markup.row(t4, t5, t6)
    markup.row(t7)
    bot.send_message(
        call.message.chat.id,  # Sửa: dùng call.message.chat.id
        "<b>Chọn số tiền ở đây nèeee!!</b>",
        parse_mode="HTML",
        reply_markup=markup  # Thêm reply_markup
    )

# Xử lý lựa chọn số tiền
@bot.callback_query_handler(func=lambda call: call.data in ["10k", "20k", "50k", "100k", "200k", "500k", "khac"])
def luachontien(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    if call.data == "khac":
        # Gửi tin nhắn với ForceReply
        msg = bot.send_message(
            call.message.chat.id,
            "Vui lòng nhập số tiền bạn muốn nạp:",
            parse_mode="HTML",
            reply_markup=ForceReply(selective=True)
        )
        bot.register_next_step_handler(msg, lay_thong_tin)
    else:
        # Lấy số tiền từ call.data (ví dụ: "10k" -> 10000)
        so_tien = int(call.data.replace("k", "000"))
        confirm_amount(call.message, so_tien)

def lay_thong_tin(message):
    try:
        text = message.text.strip().lower()  # Chuẩn hóa: xóa khoảng trắng, chuyển thành chữ thường
        if text.endswith('k'):  # Kiểm tra nếu nhập dạng "15k"
            so_tien = int(float(text[:-1]) * 1000)  # Loại "k", nhân với 1000
        else:
            so_tien = int(text)  # Chuyển trực tiếp thành số nguyên
        if so_tien <= 0:
            bot.send_message(message.chat.id, "<b>Số tiền phải lớn hơn 0!</b>", parse_mode="HTML")
            return
        confirm_amount(message, so_tien)
    except ValueError:
        bot.send_message(message.chat.id, "<b>Số tiền không hợp lệ! Vui lòng nhập số nguyên (ví dụ: 15000) hoặc định dạng 'k' (ví dụ: 15k).</b>", parse_mode="HTML")

# Xác nhận số tiền
def confirm_amount(message, so_tien):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Đồng ý", callback_data=f"confirm_{so_tien}"),
               InlineKeyboardButton("Hủy", callback_data="cancel"))
    bot.send_message(message.chat.id, f"Bạn muốn nạp {so_tien:,} VNĐ?", reply_markup=markup)

# Xử lý callback từ nút "Đồng ý" hoặc "Hủy"
user_data = {} 
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_") or call.data == "cancel")
def naptien(call):
    user_id = call.from_user.id
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data.startswith("confirm_"):
        so_tien = int(call.data.split("_")[1])
        user_data[user_id] = {"so_tien": so_tien}

        # Gửi tin nhắn yêu cầu nội dung chuyển khoản với ForceReply
        msg = bot.send_message(
            call.message.chat.id,
            "💬 Vui lòng nhập nội dung chuyển khoản:",
            parse_mode="HTML",
            reply_markup=ForceReply(selective=True)
        )
        bot.register_next_step_handler(msg, handle_user_input)  # Đăng ký hàm xử lý nội dung
    
    elif call.data == "cancel":
        bot.send_message(call.message.chat.id, "❌ Đã hủy!")
        if user_id in user_data:
            del user_data[user_id]  # Xóa dữ liệu tạm nếu hủy

# Hàm gửi thông tin số tiền và nội dung đến nhóm chat qua bot B
def send_to_group_chat(user, so_tien, noi_dung):
    # Tạo tin nhắn thông báo
    message_text = (
        f"Thông tin chuyển khoản mới:\n"
        f"Tên: {user.full_name}\n"
        f"ID: {user.id}\n"
        f"Số tiền: {so_tien:,} VNĐ\n"
        f"Nội dung: {noi_dung}"
    )

    # Gửi tin nhắn qua API Telegram
    url = f"https://api.telegram.org/bot{BOT_B_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID_B,
        'text': message_text,
        'parse_mode': 'HTML'  # Hỗ trợ định dạng nếu cần
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Lỗi khi gửi tin nhắn đến nhóm: HTTP {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Lỗi khi gửi tin nhắn đến nhóm: {e}")

# Xử lý nội dung chuyển khoản từ người dùng
@bot.message_handler(func=lambda message: message.from_user.id in user_data)
def handle_user_input(message):
    user_id = message.from_user.id
    data = user_data.pop(user_id)  # Lấy và xóa thông tin tạm
    so_tien = data["so_tien"]
    noi_dung = message.text.strip()
    user = message.from_user

    if not noi_dung:
        bot.send_message(message.chat.id, "<b>Nội dung chuyển khoản không được để trống!</b>", parse_mode="HTML")
        return

    # Tạo QR Code
    link = qrlink(STK, BANK, so_tien, noi_dung, "true")  # Sử dụng STK và BANK
    dinh_dang_so_tien = f"{so_tien:,}".replace(",", ".")

    noi_dung_thong_tin = (
        f"<b>➤ THÔNG TIN QRCODE !!!\n"
        f"┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┣➤ 🏦 Ngân Hàng: {BANK.upper()}\n"
        f"┣➤ 💳 Số TK: <code>{STK}</code>\n"
        f"┣➤ 💵 Số tiền: {dinh_dang_so_tien} VNĐ\n"
        f"┣➤ 📋 Nội dung: <code>{noi_dung}</code>\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━┛</b>\n"
    )

    # Gửi ảnh QR đến người dùng
    response = requests.get(link)
    if response.status_code == 200:
        bot.send_photo(message.chat.id, response.content, caption=noi_dung_thong_tin, parse_mode="HTML")
        # Gửi thông tin đến nhóm chat qua bot B
        send_to_group_chat(user, so_tien, noi_dung)
    else:
        bot.send_message(message.chat.id, f"<b>Không thể tải QR code. Lỗi: HTTP {response.status_code}</b>", parse_mode="HTML")
# Chạy bot
if __name__ == "__main__":
    print("Bot đang hoạt động ...\n")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Lỗi trong quá trình polling: {e}")