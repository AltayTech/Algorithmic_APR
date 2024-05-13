# -*- coding: utf-8 -*-
import pdfplumber
import re
import rpack
import cv2
import pytesseract

print('sdfsdfsadfsdfsa')

from wand.image import Image as WandImage
from PIL import Image, ImageDraw



pdf_path = 'assets\\test_page190.pdf'

# config parameter
number_of_option = 4
number_of_column = 0
question_margin_top = 5
question_margin_bottom = 5
question_margin_left = 5
question_margin_right = 1


def extract_text_with_coords(image_path):
    """
    Reads an image, extracts text with bounding box coordinates,
    and returns a list of (text, x1, y1, x2, y2) tuples.

    Args:
        image_path (str): Path to the image file.

    Returns:
        list: A list of tuples containing the extracted text and its coordinates.
    """

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Handle potential noise and uneven lighting
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    blur = cv2.GaussianBlur(thresh, (3, 3), 0)

    # Detect text regions using adaptive thresholding
    text_contours = cv2.findContours(blur, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    text_data = []
    for contour in text_contours:
        x, y, w, h = cv2.boundingRect(contour)

        # Extract text using Tesseract OCR
        text = pytesseract.image_to_string(img[y:y+h, x:x+w], config='--psm 6')

        # If text is not empty, append data
        if text:
            text_data.append((text.strip(), x, y, x+w, y+h))

    return text_data

# Detect the target rectangule is in main rect or not
def is_in_the_region(mainRect, targetRect):
    in_region = False
    if (mainRect[2] - targetRect[2]) > -5 and (targetRect[0] - mainRect[0]) > -5:
        if (mainRect[3] - targetRect[3]) > -5 and (targetRect[1] - mainRect[1]) > -5:
            in_region = True
        else:
            in_region = False

    else:
        in_region = False
    return in_region


def is_in_horizontal_region(mainRect, targetRect):
    in_region = False
    if (mainRect[2] - targetRect[2]) > -5 and (targetRect[0] - mainRect[0]) > -5:
        if (mainRect[3] - targetRect[3]) > -5 and (targetRect[1] - mainRect[1]) > -5:
            in_region = True
        else:
            in_region = False

    else:
        in_region = False
    return in_region


# Detect target rect is in the right of main rect or not
def is_in_right(mainRect, targetRect):
    in_right = False

    if (targetRect[0] - mainRect[0]) > 1:

        in_right = True
    else:
        in_right = False
    return in_right


# Detect target rect is in the below of main rect or not

def is_in_blew(mainRect, targetRect):
    in_blew = False

    if (targetRect[1] - mainRect[1]) > 1:

        in_blew = True
    else:
        in_blew = False
    return in_blew


# PDF'ten metin içeriği ve metinlerin koordinatlarını çıkar
with pdfplumber.open(pdf_path) as pdf:
    detected_question_numbers_general = {}
    detect_question = {}
    all_boxes = []
    detected_options = {}
    detected_options_box = []



    pdf.open(pdf_path)

    # Döküman boyutlarını ekrana basma
    print(f"Döküman Boyutları: Genişlik: {pdf.pages[0].width}, Yükseklik: {pdf.pages[0].height}")

    # İlk sayfa için metin içeriği ve metinlerin koordinatlarını çıkarma
    page = pdf.pages[0]
    extracted_texts_with_coords = page.extract_words()

    for item in extracted_texts_with_coords:
        # print(f"item index: {item}")
        detected_options = {}

        text = item['text'].strip()  # Boşlukları temizleme
        x0, y0, x1, y1 = item['x0'], item['top'], item['x1'], item['bottom']
        all_boxes.append((x0, y0, x1, y1))

        if re.match(r"^[1-9][0-9]{0,2}\.$", text) and 1 <= int(text[:-1]) <= 120:
            # print(f"item index: {text}")

            detected_question_numbers_general[text] = (x0, y0, x1, y1)
            # print(f"item detected_question_numbers_general: {detected_question_numbers_general[text]}")

        # A, B, C, D, E seçeneklerini tespit etme
        if re.match(r"^\s?[ABCDE]\s?\)$", text):
            detected_options[text] = (x0, y0, x1, y1)
            # print(f"detected_options: {detected_options}")
            detected_options_box.append(detected_options)

    # Determine the last option item(D orE)

    if number_of_option == 4:
        last_option = 'D)'
    else:
        last_option = 'E)'

    # Determine the last option item(D or E)
    for item in detected_question_numbers_general:

        x0, y0, x1, y1 = (detected_question_numbers_general[item][0], detected_question_numbers_general[item][1],
                          pdf.pages[0].width - 10,
                          pdf.pages[0].height - 10)
        detect_question[item] = (x0, y0, x1, y1)
        nextHorizontalQuestionX = x1
        nexVerticallyQuestionY = y1

        for item2 in detected_question_numbers_general:
            if is_in_right(detect_question[item], detected_question_numbers_general[item2]) and number_of_column == 2:
                nextHorizontalQuestionX = detected_question_numbers_general[item2][0] - 3
                x0, y0, x1, y1 = (detect_question[item][0], detect_question[item][1],
                                  nextHorizontalQuestionX,
                                  nexVerticallyQuestionY)
                detect_question[item] = (x0, y0, x1, y1)

            if is_in_the_region(detect_question[item], detected_question_numbers_general[item2]):
                # print(f"is_in_the_region: {detected_question_numbers_general[item2]}")

                detect_question[item] = (x0, y0, x1, y1)
                if not is_in_right(detect_question[item], detected_question_numbers_general[item2]):
                    if is_in_blew(detect_question[item], detected_question_numbers_general[item2]):
                        print(f"is_in_blew: {detected_question_numbers_general[item2]}")
                        nexVerticallyQuestionY = detected_question_numbers_general[item2][1] - 3
                        x0, y0, x1, y1 = (detect_question[item][0], detect_question[item][1],
                                          nextHorizontalQuestionX,
                                          nexVerticallyQuestionY)
                        detect_question[item] = (x0, y0, x1, y1)
                else:
                    nextHorizontalQuestionX = detected_question_numbers_general[item2][0] - 3
                    x0, y0, x1, y1 = (detect_question[item][0], detect_question[item][1],
                                      nextHorizontalQuestionX,
                                      nexVerticallyQuestionY)
                    detect_question[item] = (x0, y0, x1, y1)
        for detected_options_item in detected_options_box:
            for option_item in detected_options_item:
                if is_in_the_region(detect_question[item], detected_options_item[option_item]) \
                        and option_item == last_option:
                    nexVerticallyQuestionY = detected_options_item[option_item][3]
                    x0, y0, x1, y1 = (detect_question[item][0], detect_question[item][1],
                                      nextHorizontalQuestionX,
                                      nexVerticallyQuestionY)
                    detect_question[item] = (x0, y0, x1, y1)
        dis_item = 0
        selected_item = detect_question[item]
        for all_boxes_item in all_boxes:

            if is_in_the_region(detect_question[item], all_boxes_item):
                if dis_item < all_boxes_item[2] - detect_question[item][0]:
                    dis_item = all_boxes_item[2] - detect_question[item][0]
                    selected_item = all_boxes_item
        nextHorizontalQuestionX = selected_item[2]
        x0, y0, x1, y1 = (detect_question[item][0], detect_question[item][1],
                          nextHorizontalQuestionX,
                          nexVerticallyQuestionY)
        detect_question[item] = (x0, y0, x1, y1)

        x0, y0, x1, y1 = (
            detect_question[item][0] - question_margin_left, detect_question[item][1] - question_margin_top,
            nextHorizontalQuestionX + question_margin_right,
            nexVerticallyQuestionY + question_margin_bottom)
        detect_question[item] = (x0, y0, x1, y1)

print(f"detected_options_box: {len(detected_options_box)}")
# PDF'yi imaja dönüştürme
with WandImage(filename=pdf_path, resolution=300) as source:
    images = source.sequence
    img_page_1 = WandImage(images[0])
    img_page_1_path = "converted_image_page_1.jpg"
    img_page_1.save(filename=img_page_1_path)

# İmajı PIL ile açma ve boyutlandırma
im = Image.open(img_page_1_path)
resized_im = im.resize((int(pdf.pages[0].width), int(pdf.pages[0].height)))

# Yeniden boyutlandırılmış imaj üzerine dikdörtgen çizme
draw = ImageDraw.Draw(resized_im)
for (x0, y0, x1, y1) in all_boxes:
    draw.rectangle([(x0, y0), (x1, y1)], outline="green")

for _, (x0, y0, x1, y1) in detected_question_numbers_general.items():
    draw.rectangle([(x0, y0), (x1, y1)], outline="red")
for detected_options_item in detected_options_box:
    for _, (x0, y0, x1, y1) in detected_options_item.items():
        draw.rectangle([(x0, y0), (x1, y1)], outline="blue")

for _, (x0, y0, x1, y1) in detect_question.items():
    draw.rectangle([(x0, y0), (x1, y1)], outline="red")

# İmajı kaydetme
img_with_all_boxes_resized_path = "result_image.jpg"
resized_im.save(img_with_all_boxes_resized_path)
