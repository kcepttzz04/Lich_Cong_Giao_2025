import json
import re
import telebot
from telebot import types
from datetime import datetime
from telebot.types import ForceReply
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import json
import re
import telebot
from telebot import types
from datetime import datetime
from telebot.types import ForceReply
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import requests  # Thêm requests để gửi feedback
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
# API Telegram
API_KEY = "7862049111:AAGzOhCSQ0RvJvygQ1z85PPq6TV5P8a8xKM"
bot = telebot.TeleBot(API_KEY)
BOT_B_TOKEN = "7278566660:AAEPHsJ4-7ihpdfqctRLLGMDI5MXOFC_31M"
CHAT_ID_B = "-4712065072"
# Số tài khoản và ngân hàng
STK = "359577004"
BANK = "VIB"
# Thời gian hiện tại
def thoi_gian_hien_tai():
    return datetime.now().strftime('%H:%M:%S ngày %d/%m/%Y')
# Cấu hình logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Gửi lời chào khi /start
@bot.message_handler(commands=['start'])
def start(message):
    # Tin nhắn chào mừng
    bot.send_message(
        message.chat.id,
        "<b>👋 Chào mừng bạn đến với bot Lịch Phụng Vụ của Kcepttzz!!</b>\n"
        "Bạn có thể tra cứu lịch phụng vụ theo ngày, hôm nay hoặc tháng.",
        parse_mode='HTML'
    )

    # Tin nhắn chứa nút
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Menu", callback_data="menu")
    btn2 = types.InlineKeyboardButton("Nhận xét về bot", callback_data="danhgia")
    btn3 = types.InlineKeyboardButton("zzDonate meee<333zz", callback_data="donate")
    markup.row(btn1)
    markup.row(btn2, btn3)

    bot.send_message(
        message.chat.id,
        "<b>🧭 Hãy chọn chức năng bạn cần bên dưới:</b>",
        parse_mode='HTML',
        reply_markup=markup
    )
def send_menu(chat_id, message_id=None):
    if message_id:
        bot.delete_message(chat_id=chat_id, message_id=message_id)

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🗓 Tra lịch hôm nay", callback_data="homnay")
    btn2 = types.InlineKeyboardButton("🗓 Tra lịch theo ngày", callback_data="ngay")
    btn3 = types.InlineKeyboardButton("🗓 Tra lịch theo tháng", callback_data="time")
    markup.row(btn1)
    markup.row(btn2, btn3)

    bot.send_message(
        chat_id,
        "<b>🧭 Hãy chọn chức năng bạn cần bên dưới:</b>",
        parse_mode='HTML',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "menu")
def callback_menu(call):
    send_menu(chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "homnay")
def homnay(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)
    try:
        # Dòng cần sửa: Dùng "%-d/%-m" để loại bỏ số 0 ở đầu tháng trên Linux (Railway)
        today = datetime.now().strftime("%-d/%-m") # <-- Dòng này đã được sửa

        # Không cần thay đổi điều kiện so sánh, vì bạn đang so sánh với muc["ngay"]["slash"]
        # which is "27/6" and matches "%-d/%-m" output for June 27th.
        for muc in lich_phung_vu:
            if muc["ngay"]["slash"] == today: # Giữ nguyên so sánh với 'slash'
                noidung = (
                    f"🗓 <b>Lịch phụng vụ hôm nay ({muc['ngay']['original']})</b>\n"
                    f"🕊️ {muc['loai_le']}\n"
                    f"✨ {muc['ten_le']}\n"
                    f"📖 Bài đọc: {muc['bai_doc']}"
                )
                bot.send_message(call.message.chat.id, noidung, parse_mode="HTML")
                break
        else:
            bot.send_message(call.message.chat.id, f"⚠️ Không tìm thấy thông tin cho ngày {today}.", parse_mode='HTML')
    except Exception as e:
        bot.send_message(call.message.chat.id, f"<b>Lỗi xảy ra: {e}</b>", parse_mode='HTML')

    # 👉 Gửi lại menu sau khi trả lời xong
    send_menu(chat_id=call.message.chat.id)


# Gửi hướng dẫn khi /help
# @bot.message_handler(commands=['help'])
# def help(message):
#    bot.send_message(message.chat.id,
#       "📌 Chỉ cần nhập ngày tháng theo định dạng <b>dd/mm</b>.\n"
#        "Ví dụ: <b>25/12</b> để xem lễ Giáng Sinh.",
#       parse_mode='HTML'
#   )
@bot.callback_query_handler(func=lambda call: call.data == "ngay")
def chon_ngay(call):
    bot.answer_callback_query(call.id)
    # Gửi tin nhắn có ForceReply
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    tin_nhan = bot.send_message(
        call.message.chat.id, 
        "<b>📅 Vui lòng nhập ngày để tìm kiếm:</b>", 
        parse_mode="HTML",
        reply_markup=ForceReply(selective=False)  # Không cần selective=True trừ khi bạn có group
    )
    bot.register_next_step_handler(tin_nhan, xu_ly_ngay)
def xu_ly_ngay(message):
    ngay_thang = message.text.strip()

    if not re.match(r"^\s*\d{1,2}[-/\.]\d{1,2}\s*$", ngay_thang):
        bot.send_message(message.chat.id, "❌ Định dạng không hợp lệ. Vui lòng nhập theo dạng <b>dd/mm</b> (vd: 01/01, 1-1, 1.1).", parse_mode='HTML')
        return

    ngay_thang = re.sub(r"[-\.]", "/", ngay_thang)
    parts = ngay_thang.split("/")
    if len(parts) == 2:
        ngay_thang = f"{int(parts[0]):02}/{int(parts[1]):02}"

    for muc in lich_phung_vu:
        if muc["ngay"]["slash"] == f"{int(parts[0])}/{int(parts[1])}":
            phan_hoi = (
                f"🗓 <b>Ngày:</b> {muc['ngay']['original']}\n"
                f"🕊️ <b>Loại lễ:</b> {muc['loai_le']}\n"
                f"✨ <b>Tên lễ:</b> {muc['ten_le']}\n"
                f"📖 <b>Bài đọc:</b> {muc['bai_doc']}"
            )
            bot.send_message(message.chat.id, phan_hoi, parse_mode='HTML')
            return

    bot.send_message(message.chat.id, "⚠️ Không tìm thấy thông tin cho ngày này.", parse_mode='HTML')
# Tải dữ liệu JSON
def load_lich_phung_vu(file_path='lichphungvuzz.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print("Lỗi khi đọc file:", e)
        return []

lich_phung_vu = load_lich_phung_vu()


@bot.callback_query_handler(func=lambda call: call.data == "time")
def chon_thang(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    markup = types.InlineKeyboardMarkup()
    trong = InlineKeyboardButton("Lễ trọng", callback_data="trong")
    nho = InlineKeyboardButton("Lễ nhớ", callback_data="nho")
    markup.row(trong,nho)
    bot.send_message(
        call.message.chat.id,
        "<b>🗓 Chọn loại lễ bạn muốn tra cứu:</b>",
        parse_mode='HTML',
        reply_markup=markup
    )
@bot.callback_query_handler(func=lambda call: call.data == "trong")
def chon_thang_trong(call):  # Đổi tên function tránh trùng
    bot.answer_callback_query(call.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    thang_hien_tai = datetime.now().month
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton(f"Tháng {i}", callback_data=f"chon_thang_trong_{i}")
        for i in range(thang_hien_tai, 13)
    ]
    keyboard.add(*buttons)

    bot.send_message(call.message.chat.id, "📅 Chọn tháng bạn muốn xem lễ trọng:", reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call: call.data.startswith("chon_thang_trong_"))
def hien_le_trong_thang(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    thang_duoc_chon = int(call.data.split("_")[-1])
    nam_hien_tai = datetime.now().year

    le_trong_thang = []

    for muc in lich_phung_vu:
        try:
            ngay_str = muc["ngay"]["slash"] + f"/{nam_hien_tai}"
            ngay = datetime.strptime(ngay_str, "%d/%m/%Y")

            if muc.get("loai_le", "").lower().strip() == "lễ trọng" and ngay.month == thang_duoc_chon:
                le_trong_thang.append({"ngay": ngay, "ten": muc["ten_le"]})
        except Exception as e:
            print("Lỗi ngày:", muc.get("ngay"), e)

    if le_trong_thang:
        tin_nhan = f"📅 Các lễ trọng trong tháng {thang_duoc_chon}:\n"
        for muc in sorted(le_trong_thang, key=lambda x: x["ngay"]):
            tin_nhan += f"🔸 {muc['ngay'].strftime('%d-%m-%Y')}: {muc['ten']}\n"
    else:
        tin_nhan = f"❌ Không có lễ trọng nào trong tháng {thang_duoc_chon}."

    bot.send_message(call.message.chat.id, tin_nhan)

@bot.callback_query_handler(func=lambda call: call.data == "nho")
def thang_nho(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    thang_hientai = datetime.now().month
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton(f"Tháng {i}", callback_data=f"chon_thang_nho_{i}")
        for i in range(thang_hientai, 13)
    ]
    keyboard.add(*buttons)
    bot.send_message(call.message.chat.id, "📅 Chọn tháng bạn muốn xem lễ nhớ:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("chon_thang_nho_"))
def chon_thang_nho(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    thang_duoc_chon = int(call.data.split("_")[-1])
    nam_hien_tai = datetime.now().year

    le_nho_thang = []

    for muc in lich_phung_vu:
        try:
            ngay_str = muc["ngay"]["slash"] + f"/{nam_hien_tai}"
            ngay = datetime.strptime(ngay_str, "%d/%m/%Y")

            if muc.get("loai_le", "").lower().strip() == "lễ nhớ" and ngay.month == thang_duoc_chon:
                le_nho_thang.append({"ngay": ngay, "ten": muc["ten_le"]})
        except Exception as e:
            print("Lỗi ngày:", muc.get("ngay"), e)

    if le_nho_thang:
        tin_nhan = f"📅 Các lễ nhớ trong tháng {thang_duoc_chon}:\n"
        for muc in sorted(le_nho_thang, key=lambda x: x["ngay"]):
            tin_nhan += f"🔹 {muc['ngay'].strftime('%d-%m-%Y')}: {muc['ten']}\n"
    else:
        tin_nhan = f"❌ Không có lễ nhớ nào trong tháng {thang_duoc_chon}."

    bot.send_message(call.message.chat.id, tin_nhan)

def rate(chat_id, message_id=None):
    if message_id:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    keyboard = [
        [InlineKeyboardButton("⭐ 1", callback_data='1'),
         InlineKeyboardButton("⭐ 2", callback_data='2')],
        [InlineKeyboardButton("⭐ 3", callback_data='3'),
         InlineKeyboardButton("⭐ 4", callback_data='4')],
        [InlineKeyboardButton("⭐ 5", callback_data='5')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        chat_id=chat_id,
        text='Bạn chấm bot mấy sao? Nhớ chấm nhẹ tay nhưng đậm tình nha!',
        reply_markup=reply_markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "danhgia")
def danhgia(call):
    rate(chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.message_handler(commands=['rate'])
def commandrate(message):
    rate(chat_id=message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data in ['1', '2', '3', '4', '5'])
def handle_rating(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    
    # Lưu rating vào user_data
    user_id = call.from_user.id
    if not hasattr(bot, 'user_data'):
        bot.user_data = {}
    bot.user_data[user_id] = {'rating': call.data, 'waiting_for_feedback': True}
    
    bot.send_message(
        call.message.chat.id,
        f"Cảm ơn bạn đã đánh giá {call.data} ⭐!\nCó gì góp ý nhẹ nhàng thì nói với bot nha, bot hứa không buồn đâu~ 😳💕",
        reply_markup=ForceReply(selective=False)
    )
    # Đăng ký xử lý nhận xét
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, receive_feedback)

def receive_feedback(message):
    user_id = message.from_user.id
    feedback = message.text
    user = message.from_user
    rating = bot.user_data.get(user_id, {}).get('rating', 'Chưa có đánh giá')

    feedback_message = (
        f"Nhận xét từ người dùng:\n"
        f"Tên: {user.full_name}\n"
        f"ID: {user.id}\n"
        f"Đánh giá: {rating} sao\n"
        f"Nhận xét: {feedback}"
    )

    url = f"https://api.telegram.org/bot{BOT_B_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID_B,
        'text': feedback_message
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        bot.send_message(message.chat.id, "Cảm ơn bạn đã để lại nhận xét!")
    except requests.RequestException as e:
        logger.error(f"Lỗi khi gửi nhận xét: {e}")
        bot.send_message(message.chat.id, "Xin lỗi, có lỗi xảy ra khi gửi nhận xét của bạn.")
    
    # Xóa trạng thái chờ nhận xét
    if user_id in bot.user_data:
        bot.user_data[user_id]['waiting_for_feedback'] = False
# Hàm tạo liên kết QR
def qrlink(STK, BANK, so_tien, noi_dung, download):
    qrlink = f"https://qr.sepay.vn/img?acc={STK}&bank={BANK}&amount={so_tien}&des={noi_dung}&template=compact&download={download}"
    return qrlink



        
# def donatee(chat_id, message_id=None):
#     if message_id:  # Chỉ xóa nếu có message_id
#         bot.delete_message(chat_id=chat_id, message_id=message_id)

#     markup = InlineKeyboardMarkup()
#     t1 = InlineKeyboardButton("10.000", callback_data="10k")
#     t2 = InlineKeyboardButton("20.000", callback_data="20k")
#     t3 = InlineKeyboardButton("50.000", callback_data="50k")
#     t4 = InlineKeyboardButton("100.000", callback_data="100k")
#     t5 = InlineKeyboardButton("200.000", callback_data="200k")
#     t6 = InlineKeyboardButton("500.000", callback_data="500k")
#     t7 = InlineKeyboardButton("Số Khác", callback_data="khac")
#     markup.row(t1, t2, t3)
#     markup.row(t4, t5, t6)
#     markup.row(t7)

#     bot.send_message(
#         chat_id,
#         "<b>Chọn số tiền ở đây nèeee!!</b>",
#         parse_mode="HTML",
#         reply_markup=markup
#     )
        
# # Xử lý nút "Donate"
# @bot.callback_query_handler(func=lambda call: call.data == "donate")
# def donate(call):
#     donatee(call.message.chat.id, call.message.message_id)
#     bot.answer_callback_query(call.id)

# @bot.message_handler(commands=['donate'])
# def command_donate(message):
#     donatee(message.chat.id)  # Không truyền message_id -> không xóa gì
# # Xử lý lựa chọn số tiền
# @bot.callback_query_handler(func=lambda call: call.data in ["10k", "20k", "50k", "100k", "200k", "500k", "khac"])
# def luachontien(call):
#     bot.answer_callback_query(call.id)
#     bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

#     if call.data == "khac":
#         # Gửi tin nhắn với ForceReply
#         msg = bot.send_message(
#             call.message.chat.id,
#             "Vui lòng nhập số tiền bạn muốn nạp:",
#             parse_mode="HTML",
#             reply_markup=ForceReply(selective=True)
#         )
#         bot.register_next_step_handler(msg, lay_thong_tin)
#     else:
#         # Lấy số tiền từ call.data (ví dụ: "10k" -> 10000)
#         so_tien = int(call.data.replace("k", "000"))
#         confirm_amount(call.message, so_tien)

# def lay_thong_tin(message):
#     try:
#         text = message.text.strip().lower()  # Chuẩn hóa: xóa khoảng trắng, chuyển thành chữ thường
#         if text.endswith('k'):  # Kiểm tra nếu nhập dạng "15k"
#             so_tien = int(float(text[:-1]) * 1000)  # Loại "k", nhân với 1000
#         else:
#             so_tien = int(text)  # Chuyển trực tiếp thành số nguyên
#         if so_tien <= 0:
#             bot.send_message(message.chat.id, "<b>Số tiền phải lớn hơn 0!</b>", parse_mode="HTML")
#             return
#         confirm_amount(message, so_tien)
#     except ValueError:
#         bot.send_message(message.chat.id, "<b>Số tiền không hợp lệ! Vui lòng nhập số nguyên (ví dụ: 15000) hoặc định dạng 'k' (ví dụ: 15k).</b>", parse_mode="HTML")

# # Xác nhận số tiền
# def confirm_amount(message, so_tien):
#     markup = InlineKeyboardMarkup()
#     markup.add(InlineKeyboardButton("Đồng ý", callback_data=f"confirm_{so_tien}"),
#                InlineKeyboardButton("Hủy", callback_data="cancel"))
#     bot.send_message(message.chat.id, f"Bạn muốn nạp {so_tien:,} VNĐ?", reply_markup=markup)

# # Xử lý callback từ nút "Đồng ý" hoặc "Hủy"
# user_data = {} 
# @bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_") or call.data == "cancel")
# def naptien(call):
#     user_id = call.from_user.id
#     bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
#     if call.data.startswith("confirm_"):
#         so_tien = int(call.data.split("_")[1])
#         user_data[user_id] = {"so_tien": so_tien}

#         # Gửi tin nhắn yêu cầu nội dung chuyển khoản với ForceReply
#         msg = bot.send_message(
#             call.message.chat.id,
#             "💬 Vui lòng nhập nội dung chuyển khoản:",
#             parse_mode="HTML",
#             reply_markup=ForceReply(selective=True)
#         )
#         bot.register_next_step_handler(msg, handle_user_input)  # Đăng ký hàm xử lý nội dung
    
#     elif call.data == "cancel":
#         bot.send_message(call.message.chat.id, "❌ Đã hủy!")
#         if user_id in user_data:
#             del user_data[user_id]  # Xóa dữ liệu tạm nếu hủy
def donatee(chat_id, message_id=None):
    if message_id:  # Chỉ xóa nếu có message_id
        bot.delete_message(chat_id=chat_id, message_id=message_id)

    # Thay InlineKeyboardMarkup bằng ReplyKeyboardMarkup
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("10.000", "20.000", "50.000")
    markup.row("100.000", "200.000", "500.000")
    markup.row("Số Khác")

    bot.send_message(
        chat_id,
        "<b><i>Bạn ơi, chọn một con số dễ thương để ủng hộ mình nha, mình cảm kích dữ lắm luôn~</i> 🐣🎁</b>",
        parse_mode="HTML",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "donate")
def donate(call):
    donatee(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['donate'])
def command_donate(message):
    donatee(message.chat.id)  # Không truyền message_id -> không xóa gì

# Xử lý lựa chọn số tiền từ ReplyKeyboardMarkup
@bot.message_handler(func=lambda message: message.text in ["10.000", "20.000", "50.000", "100.000", "200.000", "500.000", "Số Khác"])
def luachontien(message):
    # Lưu số tiền vào user_data
    if message.text == "Số Khác":
        # Gửi tin nhắn với ForceReply
        msg = bot.send_message(
            message.chat.id,
            "<i><b>Chọn một số tiền mà bạn thấy thoải mái nhất nha, mình biết ơn từng chút một luôn đó!</b></i>",
            parse_mode="HTML",
            reply_markup=ForceReply(selective=True)
        )
        bot.register_next_step_handler(msg, lay_thong_tin)
    else:
        # Lấy số tiền từ message.text (ví dụ: "10.000" -> 10000)
        so_tien = int(message.text.replace(".", ""))
        user_data[message.from_user.id] = {"so_tien": so_tien, "message": None}
        confirm_amount(message, so_tien)
def lay_thong_tin(message):
    try:
        text = message.text.strip().lower()  # Chuẩn hóa: xóa khoảng trắng, chuyển thành chữ thường
        if text.endswith('k'):  # Kiểm tra nếu nhập dạng "15k"
            so_tien = int(float(text[:-1]) * 1000)  # Loại "k", nhân với 1000
        else:
            so_tien = int(text)  # Chuyển trực tiếp thành số nguyên
        if so_tien <= 0:
            bot.send_message(message.chat.id, "<i><b> Mình biết tấm lòng bạn to lắm, nên đừng để số 0 cô đơn nha!</b></i>", parse_mode="HTML")
            return
        user_data[message.from_user.id] = {"so_tien": so_tien, "message": None}
        # Hỏi người dùng có muốn gửi lời nhắn không
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Được", "Không")
        bot.send_message(
            message.chat.id,
            "<i><b>Gửi cho mình một chiếc lời nhắn xinh xinh được hông? Mình hứa sẽ đọc thiệt chăm luôn á! </b></i>💕",parse_mode="HTML",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, handle_message_option)
    except ValueError:
        bot.send_message(message.chat.id, "<b>Ối dời ơi~ số tiền chưa đúng rồi nè! Nhập số nguyên (vd: 15000) hoặc kiểu 'k' dễ thương (vd: 15k) nha~ 💸✨.</b>", parse_mode="HTML")
# Xử lý lựa chọn "Có" hoặc "Không" cho lời nhắn
def handle_message_option(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        bot.send_message(message.chat.id, "<b>Ơ kìa~ bạn quên chọn số tiền rồi á 🥺 Nhớ gõ /donate để mình làm lại từ đầu nghen!</b>", parse_mode="HTML")
        return

    if message.text == "Được":
        msg = bot.send_message(
            message.chat.id,
            "💬<i><b>Bạn ơi, ghi cho bot một lời nhắn dễ thương đi nè~ Bot đợi chờ lắm đó!</b></i> 🥺",
            parse_mode="HTML",
            reply_markup=ForceReply(selective=True)
        )
        bot.register_next_step_handler(msg, handle_user_input)
    elif message.text == "Không":
        user_data[user_id]["message"] = ""  # Để trống nội dung
        so_tien = user_data[user_id]["so_tien"]
        confirm_amount(message, so_tien)

# Xác nhận số tiền
def confirm_amount(message, so_tien):
    # Thay InlineKeyboardMarkup bằng ReplyKeyboardMarkup
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Đồng ý", "Hủy")
    bot.send_message(message.chat.id, f"<i><b>Chắc chắn là bạn muốn nạp {so_tien:,} VNĐ cho bot đúng không?✨</b></i>", parse_mode="HTML",reply_markup=markup)

user_data = {} 
@bot.message_handler(func=lambda message: message.text in ["Đồng ý", "Hủy"])
def naptien(message):
    user_id = message.from_user.id
    if message.text == "Đồng ý":
        # Kiểm tra và lấy số tiền từ user_data
        if user_id in user_data and "so_tien" in user_data[user_id]:
            # Hỏi người dùng có muốn gửi lời nhắn không
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("Được", "Không")
            bot.send_message(
                message.chat.id,
                "<i><b>Gửi cho mình một chiếc lời nhắn xinh xinh được hông? Mình hứa sẽ đọc thiệt chăm luôn á! 💕</b></i>",
                parse_mode="HTML",
                reply_markup=markup
)
            bot.register_next_step_handler(message, handle_message_option_naptien)
        else:
            bot.send_message(message.chat.id, "<b>Ơ kìa~ bạn quên chọn số tiền rồi á 🥺 Nhớ gõ /donate để mình làm lại từ đầu nghen!</b>", parse_mode="HTML")
    
    elif message.text == "Hủy":
        bot.send_message(message.chat.id, "<b>❌ Ôi, bạn hủy rồi à? Không sao đâu, bot vẫn yêu bạn mà! 🥺💖</b>", parse_mode="HTML")
        if user_id in user_data:
            del user_data[user_id]  # Xóa dữ liệu tạm nếu hủy

def handle_message_option_naptien(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        bot.send_message(message.chat.id, "<i><b> Ơ kìa~ bạn quên chọn số tiền rồi á 🥺 Nhớ gõ /donate để mình làm lại từ đầu nghen!</b></i>", parse_mode="HTML")
        return

    if message.text == "Được":
        msg = bot.send_message(
            message.chat.id,
            "<i><b>Để lại lời nhắn yêu thương của bạn ở đây đi nè~ Bot sẽ rất cảm ơn bạn luôn á! 💖✨</b></i>",
            parse_mode="HTML",
            reply_markup=ForceReply(selective=True)
        )
        bot.register_next_step_handler(msg, handle_user_input)
    elif message.text == "Không":
        user_data[user_id]["message"] = ""  # Để trống nội dung
        handle_user_input(message)  # Gọi thẳng handle_user_input với nội dung rỗng


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

@bot.message_handler(func=lambda message: message.from_user.id in user_data)
def handle_user_input(message):
    user_id = message.from_user.id
    data = user_data.pop(user_id)  # Lấy và xóa thông tin tạm
    so_tien = data["so_tien"]
    # Kiểm tra nếu người dùng vừa nhập nội dung (bấm "Có"), thì lấy từ message.text
    # Nếu không, lấy từ data["message"] (bấm "Không")
    if message.text:  # Trường hợp người dùng vừa nhập nội dung
        noi_dung = message.text.strip()
    else:  # Trường hợp bấm "Không" hoặc không có nội dung mới
        noi_dung = data.get("message", "")

    user = message.from_user

    # Tạo QR Code
    link = qrlink(STK, BANK, so_tien, noi_dung, "true")  # Sử dụng STK và BANK
    dinh_dang_so_tien = f"{so_tien:,}".replace(",", ".")

    noi_dung_thong_tin = (
        f"<b> Cảm ơn bạn, sự hỗ trợ của bạn có ý nghĩa rất lớn với mình!!!</b>\n"
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
# # Xử lý nội dung chuyển khoản từ người dùng
# @bot.message_handler(func=lambda message: message.from_user.id in user_data)
# def handle_user_input(message):
#     user_id = message.from_user.id
#     data = user_data.pop(user_id)  # Lấy và xóa thông tin tạm
#     so_tien = data["so_tien"]
#     noi_dung = message.text.strip()
#     user = message.from_user

#     if not noi_dung:
#         bot.send_message(message.chat.id, "<b>Nội dung chuyển khoản không được để trống!</b>", parse_mode="HTML")
#         return

#     # Tạo QR Code
#     link = qrlink(STK, BANK, so_tien, noi_dung, "true")  # Sử dụng STK và BANK
#     dinh_dang_so_tien = f"{so_tien:,}".replace(",", ".")

#     noi_dung_thong_tin = (
#         f"<b>➤ THÔNG TIN QRCODE !!!\n"
#         f"┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"
#         f"┣➤ 🏦 Ngân Hàng: {BANK.upper()}\n"
#         f"┣➤ 💳 Số TK: <code>{STK}</code>\n"
#         f"┣➤ 💵 Số tiền: {dinh_dang_so_tien} VNĐ\n"
#         f"┣➤ 📋 Nội dung: <code>{noi_dung}</code>\n"
#         f"┗━━━━━━━━━━━━━━━━━━━━━━━┛</b>\n"
#     )

#     # Gửi ảnh QR đến người dùng
#     response = requests.get(link)
#     if response.status_code == 200:
#         bot.send_photo(message.chat.id, response.content, caption=noi_dung_thong_tin, parse_mode="HTML")
#         # Gửi thông tin đến nhóm chat qua bot B
#         send_to_group_chat(user, so_tien, noi_dung)
#     else:
#         bot.send_message(message.chat.id, f"<b>Không thể tải QR code. Lỗi: HTTP {response.status_code}</b>", parse_mode="HTML")
    
@bot.message_handler(commands=['huongdan'])
def huongdan(message):
    bot.send_message(
        message.chat.id,
        "<b>📌 Hướng dẫn sử dụng bot </b>",parse_mode="HTML"
    )
# Chạy bot
if __name__ == "__main__":
    print("🤖 Bot đang hoạt động...")
    bot.infinity_polling()
