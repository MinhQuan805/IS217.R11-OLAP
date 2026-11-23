import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Colors
    BG_DARK = RGBColor(11, 19, 43)        # #0B132B Deep Dark Slate/Navy
    CARD_BG = RGBColor(22, 32, 58)        # #16203A Card background
    CARD_BORDER = RGBColor(42, 59, 92)    # #2A3B5C Subtle border
    CARD_BG_LIGHT = RGBColor(30, 41, 68)  # #1E2944 Slightly lighter card
    
    TEXT_WHITE = RGBColor(255, 255, 255)
    TEXT_LIGHT = RGBColor(226, 232, 240)  # #E2E8F0 Soft light slate
    TEXT_MUTED = RGBColor(148, 163, 184)  # #94A3B8 Muted slate
    
    CYAN_ACCENT = RGBColor(56, 189, 248)  # #38BDF8 Sky Cyan
    GREEN_ACCENT = RGBColor(16, 185, 129) # #10B981 Emerald
    AMBER_ACCENT = RGBColor(245, 158, 11) # #F59E0B Warm Amber
    PURPLE_ACCENT = RGBColor(167, 139, 250) # #A78BFA Violet
    ROSE_ACCENT = RGBColor(244, 63, 94)   # #F43F5E Rose

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, section_tag, title_text, slide_num, total_slides=15):
        # Section Tag Pill
        tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(0.4), Inches(4.2), Inches(0.36))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = CARD_BG
        tag_box.line.color.rgb = CYAN_ACCENT
        tag_box.line.width = Pt(1.2)
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = False
        tf_tag.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = f"  {section_tag.upper()}  "
        p_tag.font.name = "Segoe UI"
        p_tag.font.size = Pt(10.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = CYAN_ACCENT

        # Slide Number Badge
        num_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.1), Inches(0.4), Inches(1.5), Inches(0.36))
        num_box.fill.solid()
        num_box.fill.fore_color.rgb = CARD_BG
        num_box.line.color.rgb = CARD_BORDER
        tf_num = num_box.text_frame
        tf_num.word_wrap = False
        tf_num.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_num = tf_num.paragraphs[0]
        p_num.text = f"SLIDE {slide_num:02d} / {total_slides:02d}"
        p_num.font.name = "Segoe UI"
        p_num.font.size = Pt(10.5)
        p_num.font.bold = True
        p_num.font.color.rgb = TEXT_MUTED
        p_num.alignment = PP_ALIGN.CENTER

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.65), Inches(0.82), Inches(11.9), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = "Segoe UI"
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.7), Inches(7.0), Inches(11.9), Inches(0.35))
        tf_footer = footer_box.text_frame
        p_footer = tf_footer.paragraphs[0]
        p_footer.text = "IS217.R11 - Đồ án Kho dữ liệu & OLAP: Tuyển sinh ĐH-CĐ (2010 - 2025)  |  GVHD: ThS. Đỗ Thị Minh Phụng  |  Nhóm: Cao Thái Bảo - Võ Minh Quân"
        p_footer.font.name = "Segoe UI"
        p_footer.font.size = Pt(9.5)
        p_footer.font.color.rgb = RGBColor(100, 116, 139)

    def add_card(slide, left, top, width, height, title=None, title_color=CYAN_ACCENT, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.22)
        tf.margin_right = Inches(0.22)
        tf.margin_top = Inches(0.2)
        tf.margin_bottom = Inches(0.2)
        
        if title:
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = "Segoe UI"
            p.font.size = Pt(15.5)
            p.font.bold = True
            p.font.color.rgb = title_color
            p.space_after = Pt(8)
        return card, tf

    def add_bullet(tf, bold_prefix, text, font_size=13.5, text_color=TEXT_LIGHT, prefix_color=CYAN_ACCENT, space_after=6):
        p = tf.add_paragraph()
        p.space_after = Pt(space_after)
        if bold_prefix:
            r1 = p.add_run()
            r1.text = "• " + bold_prefix + ": "
            r1.font.name = "Segoe UI"
            r1.font.bold = True
            r1.font.size = Pt(font_size)
            r1.font.color.rgb = prefix_color
        else:
            r1 = p.add_run()
            r1.text = "• "
            r1.font.name = "Segoe UI"
            r1.font.bold = True
            r1.font.size = Pt(font_size)
            r1.font.color.rgb = prefix_color
            
        r2 = p.add_run()
        r2.text = text
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(font_size)
        r2.font.color.rgb = text_color

    def add_metric_box(slide, left, top, width, height, number_str, label_str, num_color=CYAN_ACCENT):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = CARD_BORDER
        box.line.width = Pt(1.2)
        
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p1 = tf.paragraphs[0]
        p1.text = number_str
        p1.font.name = "Segoe UI"
        p1.font.size = Pt(26)
        p1.font.bold = True
        p1.font.color.rgb = num_color
        p1.alignment = PP_ALIGN.CENTER
        
        p2 = tf.add_paragraph()
        p2.text = label_str
        p2.font.name = "Segoe UI"
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = TEXT_MUTED
        p2.alignment = PP_ALIGN.CENTER

    def add_speaker_notes(slide, notes):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    
    # Decorative accent bar
    accent_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(0.12), Inches(4.8))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = CYAN_ACCENT
    accent_bar.line.fill.background()
    
    # Title Box
    title_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.1), Inches(11.0), Inches(4.9))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN - ĐHQG-HCM"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT
    p.space_after = Pt(4)
    
    p = tf1.add_paragraph()
    p.text = "KHOA HỆ THỐNG THÔNG TIN  |  MÔN HỌC: KHO DỮ LIỆU & OLAP (IS217.R11)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(22)
    
    p = tf1.add_paragraph()
    p.text = "XÂY DỰNG KHO DỮ LIỆU VÀ HỆ THỐNG OLAP\nPHÂN TÍCH TÌNH HÌNH TUYỂN SINH ĐẠI HỌC, CAO ĐẲNG\nTẠI VIỆT NAM GIAI ĐOẠN 2010 - 2025"
    p.font.name = "Segoe UI"
    p.font.size = Pt(27)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(28)
    
    p = tf1.add_paragraph()
    p.text = "👨‍🏫 Giảng viên hướng dẫn: ThS. Đỗ Thị Minh Phụng"
    p.font.name = "Segoe UI"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = AMBER_ACCENT
    p.space_after = Pt(6)
    
    p = tf1.add_paragraph()
    p.text = "👨‍🎓 Sinh viên thực hiện: Cao Thái Bảo (24520145)   —   Võ Minh Quân (24521459)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT
    p.space_after = Pt(14)

    p = tf1.add_paragraph()
    p.text = "⏱ Thời lượng báo cáo: 15 Phút   |   🎯 Quy mô: End-to-End DWH + ETL + OLAP + BI + Data Mining"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    add_speaker_notes(s1, """[00:00 - 01:00] LỜI MỞ ĐẦU & GIỚI THIỆU:
Kính thưa ThS. Đỗ Thị Minh Phụng cùng toàn thể Hội đồng. Em là Cao Thái Bảo và bạn cùng nhóm là Võ Minh Quân. 
Hôm nay, nhóm chúng em xin được đại diện báo cáo đồ án môn học Kho dữ liệu và OLAP với đề tài: 
"Xây dựng kho dữ liệu và hệ thống OLAP phân tích tình hình tuyển sinh tại các trường Đại học, Học viện, Cao đẳng tại Việt Nam giai đoạn 2010 - 2025".

Bài báo cáo của nhóm được thiết kế tinh gọn trong thời lượng 15 phút, bao quát trọn vẹn 5 chương của đồ án: từ khảo sát dữ liệu, thiết kế kho chuẩn Snowflake, tích hợp ETL qua SSIS, xây dựng khối OLAP SSAS truy vấn MDX, trực quan hóa trên Power BI & Looker Studio, cho đến ứng dụng Khai phá dữ liệu với các mô hình Machine Learning tiên tiến.""")

    # =========================================================================
    # SLIDE 2: BỐI CẢNH & MỤC TIÊU ĐỀ TÀI (CHƯƠNG 1)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Chương I: Tổng Quan", "Bối Cảnh Thực Tiễn & Mục Tiêu Nghiên Cứu", 2)
    
    # 2 Big Cards
    _, tf_c1 = add_card(s2, 0.7, 1.5, 5.8, 5.2, "Bối Cảnh & Thực Trạng Tuyển Sinh", AMBER_ACCENT)
    add_bullet(tf_c1, "Bùng nổ dữ liệu tuyển sinh", "Giai đoạn 2010 - 2025 chứng kiến sự chuyển biến mạnh mẽ của giáo dục ĐH với hơn 300 trường, hàng trăm ngành đào tạo và hơn 100.000 lượt điểm chuẩn.", 14)
    add_bullet(tf_c1, "Đa dạng hóa phương thức", "Xuất hiện nhiều phương thức xét tuyển mới: Điểm thi THPT, Xét học bạ, Đánh giá năng lực (ĐGNL ĐHQG, V-ACT, H-ACT, TSA), Tuyển thẳng...", 14)
    add_bullet(tf_c1, "Tồn tại & Thách thức", "Dữ liệu phân tán, định dạng không đồng nhất, thang điểm khác biệt (thang 30, thang 40, thang 1200), gây khó khăn cho việc tra cứu và ra quyết định.", 14)
    add_bullet(tf_c1, "Nhu cầu cấp thiết", "Cần một hệ sinh thái dữ liệu hợp nhất, đa chiều giúp thí sinh chọn trường, nhà trường định vị tuyển sinh và nhà quản lý hoạch định chính sách.", 14)

    _, tf_c2 = add_card(s2, 6.8, 1.5, 5.8, 5.2, "Mục Tiêu & Đóng Góp Chính", GREEN_ACCENT)
    add_bullet(tf_c2, "Chuẩn hóa & Tích hợp (DWH)", "Xây dựng Kho dữ liệu mô hình Snowflake Schema chuẩn 3NF, xử lý triệt để quan hệ Nhiều - Nhiều (N:N) qua các bảng Bridge.", 14)
    add_bullet(tf_c2, "Tự động hóa ETL (SSIS)", "Thiết kế luồng nạp dữ liệu tuần tự với Precedence Constraints, tự động kiểm soát khóa ngoại và tính toàn vẹn dữ liệu.", 14)
    add_bullet(tf_c2, "Phân tích đa chiều (SSAS & MDX)", "Xây dựng khối OLAP Cube với 9 Dimension, cấu hình phân cấp (Hierarchies) và giải quyết 15 bài toán nghiệp vụ phức tạp bằng MDX.", 14)
    add_bullet(tf_c2, "Báo biểu trực quan (BI)", "Phát triển 6 Dashboard quản trị trực quan trên Power BI và Google Looker Studio phục vụ tra cứu đa chiều.", 14)
    add_bullet(tf_c2, "Khai phá dữ liệu (Machine Learning)", "Huấn luyện và so sánh 4 mô hình học máy (Decision Tree, XGBoost, LightGBM, Stacking) dự đoán phân khúc điểm chuẩn.", 14)

    add_speaker_notes(s2, """[01:00 - 02:00] BỐI CẢNH & MỤC TIÊU:
Bước vào Chương I, bối cảnh tuyển sinh đại học Việt Nam 15 năm qua ghi nhận sự chuyển dịch cực kỳ mạnh mẽ. Bên cạnh phương thức truyền thống là Điểm thi THPT, các trường đã mở rộng xét tuyển học bạ, đánh giá năng lực ĐHQG-HCM, ĐHQG Hà Nội, Bách Khoa...
Tuy nhiên, dữ liệu này nằm rải rác, thang điểm vênh nhau (thang 30, 40, 100, 1200). 
Mục tiêu của nhóm là xây dựng một giải pháp trọn gói: Kho dữ liệu Snowflake trên SQL Server, tích hợp ETL tự động bằng SSIS, khối phân tích đa chiều SSAS kèm 15 câu MDX, 6 báo cáo Dashboard BI và bài toán Khai phá dữ liệu dự báo điểm chuẩn.""")

    # =========================================================================
    # SLIDE 3: DỮ LIỆU NGUỒN & QUY TRÌNH LÀM SẠCH (CHƯƠNG 1)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Chương I: Dữ Liệu Nguồn & Tiền Xử Lý", "Khảo Sát Bộ Dữ Liệu & Quy Trình Làm Sạch Chuẩn Hóa", 3)
    
    # 3 Metric boxes on top
    add_metric_box(s3, 0.7, 1.5, 3.7, 1.15, "147,671", "Dòng điểm chuẩn gốc (cutoff-scores)", CYAN_ACCENT)
    add_metric_box(s3, 4.8, 1.5, 3.7, 1.15, "506", "Ngành & Nhóm ngành chuẩn (majors)", AMBER_ACCENT)
    add_metric_box(s3, 8.9, 1.5, 3.7, 1.15, "279", "Tổ hợp môn xét tuyển (score-group)", GREEN_ACCENT)

    # Lower Left Card: Quy tắc làm sạch
    _, tf_s3_l = add_card(s3, 0.7, 2.85, 5.8, 3.85, "Quy Trình Tiền Xử Lý & Làm Sạch", CYAN_ACCENT)
    add_bullet(tf_s3_l, "Lọc bỏ dữ liệu rác", "Xóa các dòng thiếu thông tin cốt lõi (điểm rỗng, mã trường không hợp lệ, điểm âm hoặc vượt ngưỡng).", 13.5)
    add_bullet(tf_s3_l, "Quy đổi thang điểm 40 về 30", "Xác định các trường/ngành nhân đôi môn chính (thang 40) và quy đổi công thức: Score_30 = (Score_40 * 3) / 4.", 13.5)
    add_bullet(tf_s3_l, "Xử lý Outlier theo IQR", "Sử dụng ngưỡng [Q1 - 1.5*IQR, Q3 + 1.5*IQR] để loại bỏ các điểm chuẩn dị biệt do lỗi nhập liệu.", 13.5)
    add_bullet(tf_s3_l, "Chuẩn hóa chuỗi văn bản", "Loại bỏ khoảng trắng thừa, đồng nhất ký tự tiếng Việt Unicode và chuẩn hóa tên phương thức tuyển sinh.", 13.5)

    # Lower Right Card: Kết quả làm sạch
    _, tf_s3_r = add_card(s3, 6.8, 2.85, 5.8, 3.85, "Định Nghĩa Khóa Hạt & Kết Quả Chuẩn Hóa", GREEN_ACCENT)
    add_bullet(tf_s3_r, "Xử lý xung đột Grain Key", "Định nghĩa khóa hạt duy nhất cho mỗi sự kiện tuyển sinh:", 13.5)
    add_bullet(tf_s3_r, "", "[School_ID, Major_Code, Program_Name, Block_Set, Year, Admission_Method]", 12.5, text_color=AMBER_ACCENT, prefix_color=AMBER_ACCENT)
    add_bullet(tf_s3_r, "Giải quyết đa mức điểm", "Với cùng một khóa hạt nếu có nhiều mức điểm, hệ thống ưu tiên mức điểm chuẩn chính thức và lọc bỏ bản ghi phụ trùng lặp.", 13.5)
    add_bullet(tf_s3_r, "Kết quả dataset sau làm sạch", "Thu được 103,403 bản ghi điểm chuẩn sạch, 506 mã ngành chuẩn và 280 tổ hợp môn được chuẩn hóa hoàn hảo sẵn sàng nạp kho.", 13.5)

    add_speaker_notes(s3, """[02:00 - 03:00] DỮ LIỆU NGUỒN & TIỀN XỬ LÝ:
Dataset đầu vào gồm 3 file CSV: File chính cutoff-scores với hơn 147 ngàn dòng, file majors với 506 ngành chuẩn của Bộ GD&ĐT, và score-group gồm 279 tổ hợp môn.
Thách thức lớn nhất ở bước tiền xử lý là:
1. Nhiều trường áp dụng thang điểm 40 (nhân đôi môn Toán hoặc Ngoại ngữ). Nhóm đã viết script phát hiện và quy đổi chính xác về thang 30.
2. Dữ liệu bị nhiễu do lỗi nhập liệu được lọc bỏ bằng phương pháp IQR.
3. Nhóm định nghĩa bộ khóa hạt Grain Key gồm 6 thuộc tính để khử triệt để xung đột dữ liệu.
Kết quả, nhóm thu được bộ dữ liệu sạch 103,403 dòng chuẩn xác.""")

    # =========================================================================
    # SLIDE 4: KIẾN TRÚC TỔNG THỂ HỆ THỐNG END-TO-END (CHƯƠNG 1)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Chương I: Kiến Trúc Hệ Thống", "Kiến Trúc Tổng Thể Hệ Thống Kho Dữ Liệu & OLAP", 4)
    
    # 4 Architecture layer cards
    layer_w = 2.8
    gap = 0.25
    top_pos = 1.6
    card_h = 5.1

    _, tf_l1 = add_card(s4, 0.7, top_pos, layer_w, card_h, "1. NGUỒN DỮ LIỆU", CYAN_ACCENT)
    add_bullet(tf_l1, "Dữ liệu thô", "Kaggle Raw Dataset & Cổng tuyển sinh.", 13)
    add_bullet(tf_l1, "Định dạng", "3 File CSV: Điểm chuẩn, Ngành học, Tổ hợp môn.", 13)
    add_bullet(tf_l1, "Quy mô", "147k+ bản ghi giai đoạn 2010 - 2025.", 13)
    add_bullet(tf_l1, "Python Script", "Làm sạch, khử trùng lặp, chuẩn hóa thang 30.", 13)

    _, tf_l2 = add_card(s4, 0.7 + layer_w + gap, top_pos, layer_w, card_h, "2. ETL & KHO DWH", AMBER_ACCENT)
    add_bullet(tf_l2, "SSIS Pipeline", "Visual Studio 2022 Integration Services.", 13)
    add_bullet(tf_l2, "Execute SQL", "Tự động hóa Drop/Create DDL.", 13)
    add_bullet(tf_l2, "Kho SQL Server", "Database ADMISSIONDATAWAREHOUSE.", 13)
    add_bullet(tf_l2, "Snowflake", "1 Fact + 9 Dim + 3 Bridge Tables.", 13)

    _, tf_l3 = add_card(s4, 0.7 + (layer_w + gap)*2, top_pos, layer_w, card_h, "3. OLAP ENGINE", PURPLE_ACCENT)
    add_bullet(tf_l3, "SSAS Multidim", "Khối Cube Admission Data Warehouse.", 13)
    add_bullet(tf_l3, "Hierarchies", "Phân cấp Tỉnh-Trường, Nhóm-Ngành.", 13)
    add_bullet(tf_l3, "Bridge Usage", "Quan hệ Many-to-Many cho Nhóm ngành & Tổ hợp.", 13)
    add_bullet(tf_l3, "MDX Analytics", "15 Câu truy vấn phân tích nghiệp vụ chuyên sâu.", 13)

    _, tf_l4 = add_card(s4, 0.7 + (layer_w + gap)*3, top_pos, layer_w, card_h, "4. BI & KHAI PHÁ", GREEN_ACCENT)
    add_bullet(tf_l4, "Power BI", "3 Dashboard xu hướng, cạnh tranh & đối sánh.", 13)
    add_bullet(tf_l4, "Looker Studio", "3 Dashboard bản đồ địa lý & biến động điểm.", 13)
    add_bullet(tf_l4, "Data Mining", "Pipeline ML phân loại 4 phân khúc điểm.", 13)
    add_bullet(tf_l4, "Mô hình tối ưu", "LightGBM đạt Accuracy 54.99% vượt trội.", 13)

    add_speaker_notes(s4, """[03:00 - 04:00] KIẾN TRÚC TỔNG THỂ:
Đây là bức tranh kiến trúc tổng thể End-to-End của hệ thống mà nhóm đã triển khai, bao gồm 4 tầng chặt chẽ:
Tầng 1: Tầng dữ liệu nguồn và tiền xử lý bằng Python.
Tầng 2: Tầng ETL và Kho dữ liệu trên SQL Server, được điều phối bằng SSIS với sơ đồ bông tuyết Snowflake.
Tầng 3: Tầng OLAP Engine trên SSAS, xây dựng khối đa chiều phục vụ ngôn ngữ truy vấn MDX với thời gian phản hồi mili-giây.
Tầng 4: Tầng Trực quan hóa và Khai phá dữ liệu với 6 báo cáo Power BI & Looker Studio cùng mô hình Machine Learning LightGBM.""")

    # =========================================================================
    # SLIDE 5: THIẾT KẾ KHO DỮ LIỆU - SƠ ĐỒ BÔNG TUYẾT (CHƯƠNG 1)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Chương I: Thiết Kế Kho Dữ Liệu", "Mô Hình Dữ Liệu Chuẩn Bông Tuyết (Snowflake Schema)", 5)
    
    # Left: Image of Snowflake schema (image73.png)
    img_path = os.path.join("key_images", "image73.png")
    if os.path.exists(img_path):
        s5.shapes.add_picture(img_path, Inches(0.7), Inches(1.5), Inches(7.5), Inches(5.2))
    
    # Right: Text Card
    _, tf_s5 = add_card(s5, 8.4, 1.5, 4.2, 5.2, "Đặc Điểm Mô Hình Bông Tuyết", CYAN_ACCENT)
    add_bullet(tf_s5, "Tên Database", "ADMISSIONDATAWAREHOUSE triển khai trên SQL Server.", 13)
    add_bullet(tf_s5, "Bảng Fact trung tâm", "FACT_CUTOFF_SCORE: Chứa khóa ngoại trỏ tới các chiều và 2 thước đo: SCORE_MARK (điểm chuẩn) & NUMBER_OF_STUDENTS (chỉ tiêu).", 13)
    add_bullet(tf_s5, "Chuẩn hóa 3NF bậc 3", "Tách nhánh phân cấp giảm dư thừa dữ liệu:", 13)
    add_bullet(tf_s5, "", "• DIM_PROVINCE -> DIM_SCHOOL\n• DIM_MAJOR_GROUP -> DIM_MAJOR -> DIM_PROGRAM\n• DIM_SUBJECT -> DIM_SCORE_BLOCK", 12, text_color=AMBER_ACCENT, prefix_color=AMBER_ACCENT)
    add_bullet(tf_s5, "9 Bảng Dimension", "Bao quát toàn diện các khía cạnh: Trường, Địa lý, Ngành, Chương trình, Tổ hợp, Môn học, Phương thức, Năm.", 13)
    add_bullet(tf_s5, "3 Bảng Bridge", "Xử lý triệt để quan hệ Nhiều - Nhiều (N:N).", 13)

    add_speaker_notes(s5, """[04:00 - 05:00] THIẾT KẾ KHO DỮ LIỆU - SNOWFLAKE:
Kính thưa Hội đồng, nhóm lựa chọn mô hình bông tuyết (Snowflake Schema) thay vì hình sao truyền thống bởi vì dữ liệu tuyển sinh có tính phân cấp rất rõ rệt:
Trường gắn với Tỉnh/Thành phố; Ngành gắn với Nhóm ngành chuẩn; và Tổ hợp môn được cấu thành từ nhiều Môn học đơn lẻ.
Bảng FACT_CUTOFF_SCORE nằm ở trung tâm lưu trữ điểm trúng tuyển. Xung quanh là 9 bảng Dimension đã được chuẩn hóa bậc 3, loại bỏ hoàn toàn hiện tượng dư thừa chuỗi tên tỉnh hoặc nhóm ngành, tiết kiệm dung lượng lưu trữ và đảm bảo tính toàn vẹn DDL.""")

    # =========================================================================
    # SLIDE 6: GIẢI PHÁP XỬ LÝ QUAN HỆ NHIỀU - NHIỀU (CHƯƠNG 1)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Chương I: Thiết Kế Kho Dữ Liệu", "Giải Pháp Xử Lý Quan Hệ Nhiều - Nhiều (Bridge Tables)", 6)
    
    # 3 Cards for 3 Bridge Tables
    b_w = 3.8
    b_gap = 0.25
    b_top = 1.55
    b_h = 5.15

    _, tf_b1 = add_card(s6, 0.7, b_top, b_w, b_h, "BRIDGE_MAJOR_GROUP", CYAN_ACCENT)
    add_bullet(tf_b1, "Bản chất quan hệ", "Quan hệ Nhiều - Nhiều giữa Ngành đào tạo (DIM_MAJOR) và Nhóm ngành (DIM_MAJOR_GROUP).", 13.5)
    add_bullet(tf_b1, "Thực tế nghiệp vụ", "Một ngành liên ngành (ví dụ: Hệ thống thông tin quản lý) vừa thuộc nhóm CNTT vừa thuộc nhóm Kinh tế quản trị.", 13.5)
    add_bullet(tf_b1, "Cấu trúc bảng", "MAJOR_ID (FK) liên kết với MAJOR_GROUP_ID (FK).", 13.5)
    add_bullet(tf_b1, "Vai trò trong Cube", "Được cấu hình làm Many-to-Many Dimension trong SSAS, giúp Roll-up điểm chuẩn chính xác.", 13.5)

    _, tf_b2 = add_card(s6, 0.7 + b_w + b_gap, b_top, b_w, b_h, "BRIDGE_SCORE_BLOCK_SUBJECT", AMBER_ACCENT)
    add_bullet(tf_b2, "Bản chất quan hệ", "Quan hệ Nhiều - Nhiều giữa Tổ hợp môn xét tuyển (DIM_SCORE_BLOCK) và từng Môn thi (DIM_SUBJECT).", 13.5)
    add_bullet(tf_b2, "Thực tế nghiệp vụ", "Một tổ hợp (như A00) gồm 3 môn Toán, Lý, Hóa; ngược lại một môn (như Toán) xuất hiện trong hàng chục tổ hợp (A00, A01, B00, D01...).", 13.5)
    add_bullet(tf_b2, "Cấu trúc bảng", "SCORE_BLOCK_ID (FK) liên kết với SUBJECT_ID (FK).", 13.5)
    add_bullet(tf_b2, "Vai trò phân tích", "Cho phép phân tích điểm chuẩn theo từng môn học thành phần.", 13.5)

    _, tf_b3 = add_card(s6, 0.7 + (b_w + b_gap)*2, b_top, b_w, b_h, "BRIDGE_FACT_SCORE_BLOCK", GREEN_ACCENT)
    add_bullet(tf_b3, "Bản chất quan hệ", "Quan hệ Nhiều - Nhiều giữa Sự kiện tuyển sinh (FACT_CUTOFF_SCORE) và Tổ hợp môn xét tuyển.", 13.5)
    add_bullet(tf_b3, "Thực tế nghiệp vụ", "Một trường xét tuyển cùng 1 mức điểm cho 3-4 tổ hợp khác nhau (ví dụ ngành CNTT xét đồng thời A00, A01, D01, D07 cùng lấy 26 điểm).", 13.5)
    add_bullet(tf_b3, "Tránh trùng Fact", "Nếu nhân bản dòng Fact cho từng tổ hợp sẽ làm sai lệch chỉ tiêu và điểm TB. Bảng Bridge lưu FACT_ID (FK) và SCORE_BLOCK_ID (FK).", 13.5)
    add_bullet(tf_b3, "Bảo toàn Measure", "Giữ Fact ở mức hạt nguyên tử chuẩn xác nhất.", 13.5)

    add_speaker_notes(s6, """[05:00 - 06:00] BẢNG BRIDGE QUAN HỆ NHIỀU - NHIỀU:
Điểm sáng tạo và phức tạp nhất trong thiết kế kho của nhóm là giải quyết triệt để 3 quan hệ Nhiều - Nhiều qua các bảng Bridge:
1. BRIDGE_MAJOR_GROUP: 1 ngành có thể thuộc nhiều nhóm ngành đào tạo.
2. BRIDGE_SCORE_BLOCK_SUBJECT: 1 tổ hợp có 3 môn và 1 môn nằm trong nhiều tổ hợp.
3. BRIDGE_FACT_SCORE_BLOCK: Đây là kỹ thuật then chốt! Khi một ngành xét cùng mức điểm cho nhiều tổ hợp môn, nếu lưu trực tiếp vào Fact sẽ làm nhân bản bản ghi, dẫn đến việc tính tổng chỉ tiêu hay điểm TB bị sai lệch gấp 3-4 lần. Nhóm tách ra bảng Bridge này để bảo toàn nguyên vẹn độ đo Fact.""")

    # =========================================================================
    # SLIDE 7: TÍCH HỢP DỮ LIỆU VỚI SSIS (ETL PIPELINE) (CHƯƠNG 2)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Chương II: Tích Hợp Dữ Liệu (ETL)", "Quy Trình ETL Tự Động Hóa Với SSIS & Ràng Buộc Ưu Tiên", 7)
    
    # Left: SSIS Image (image129.png)
    img_ssis = os.path.join("key_images", "image129.png")
    if os.path.exists(img_ssis):
        s7.shapes.add_picture(img_ssis, Inches(0.7), Inches(1.5), Inches(7.2), Inches(5.2))
        
    # Right: Text Card
    _, tf_s7 = add_card(s7, 8.1, 1.5, 4.5, 5.2, "Kiến Trúc Điều Phối Control Flow", CYAN_ACCENT)
    add_bullet(tf_s7, "Tự động hóa DDL", "Sử dụng 2 tác vụ Execute SQL Task:", 13)
    add_bullet(tf_s7, "", "• Drop All Tables: Xóa sạch theo thứ tự ngược quan hệ FK (Bridge -> Fact -> Dim).\n• Create All Tables: Tạo mới toàn bộ 13 bảng cấu trúc chuẩn.", 12, text_color=AMBER_ACCENT, prefix_color=AMBER_ACCENT)
    add_bullet(tf_s7, "13 Data Flow Tasks", "Trích xuất từ CSV sạch, thực hiện Derived Column, Data Conversion, Sort và nạp vào OLE DB Destination.", 13)
    add_bullet(tf_s7, "Precedence Constraints", "Thiết lập thứ tự nạp 4 giai đoạn nghiêm ngặt:", 13)
    add_bullet(tf_s7, "", "1. Dim Độc lập: Province, Major Group, Subject, Admission Method, Year.\n2. Dim Phụ thuộc: School, Major, Program, Score Block.\n3. Fact: FACT_CUTOFF_SCORE.\n4. Bridge: 3 Bảng Bridge N:N.", 12, text_color=GREEN_ACCENT, prefix_color=GREEN_ACCENT)
    add_bullet(tf_s7, "Kết quả thực thi", "Toàn bộ package SSIS chạy thành công (Success 100%), không xảy ra lỗi vi phạm khóa ngoại.", 13)

    add_speaker_notes(s7, """[06:00 - 07:00] TÍCH HỢP DỮ LIỆU SSIS:
Sang Chương II, để nạp dữ liệu vào kho tự động và ổn định, nhóm xây dựng gói SSIS Package trên Visual Studio 2022.
Quy trình Control Flow được thiết kế vô cùng chặt chẽ:
Đầu tiên là 2 Execute SQL Task: Drop các bảng cũ theo thứ tự từ con lên cha, và Create các bảng mới.
Tiếp theo, nhờ hệ thống ràng buộc ưu tiên Precedence Constraints, các bảng Dimension độc lập được nạp trước, sau đó tới Dimension phụ thuộc, bảng Fact và cuối cùng là 3 bảng Bridge.
Cách bố trí này giúp quá trình ETL diễn ra song song tối đa mà tuyệt đối không bao giờ gặp lỗi Foreign Key Constraint.""")

    # =========================================================================
    # SLIDE 8: XÂY DỰNG KHỐI OLAP (SSAS CUBE) (CHƯƠNG 3)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Chương III: Phân Tích Đa Chiều (OLAP)", "Xây Dựng Khối SSAS Cube, Phân Cấp & Many-to-Many", 8)
    
    # Left: SSAS Cube Image (image232.png)
    img_cube = os.path.join("key_images", "image232.png")
    if os.path.exists(img_cube):
        s8.shapes.add_picture(img_cube, Inches(0.7), Inches(1.5), Inches(7.2), Inches(5.2))
        
    # Right: Text Card
    _, tf_s8 = add_card(s8, 8.1, 1.5, 4.5, 5.2, "Cấu Trúc & Cấu Hình SSAS Cube", PURPLE_ACCENT)
    add_bullet(tf_s8, "Khối Cube hoàn chỉnh", "Cube Admission Data Warehouse tích hợp đầy đủ 13 bảng từ Data Source View (DSV).", 13)
    add_bullet(tf_s8, "Cấu hình phân cấp (Hierarchies)", "Xây dựng các cây phân cấp phục vụ thao tác Roll-up và Drill-down mượt mà:", 13)
    add_bullet(tf_s8, "", "• Địa lý: Tỉnh/Thành phố -> Trường ĐH-CĐ\n• Đào tạo: Nhóm ngành -> Ngành -> Chương trình", 12, text_color=AMBER_ACCENT, prefix_color=AMBER_ACCENT)
    add_bullet(tf_s8, "Dimension Usage Phức Tạp", "Cấu hình Dimension Many-to-Many cho DIM_MAJOR_GROUP và DIM_SCORE_BLOCK thông qua các bảng Bridge tương ứng.", 13)
    add_bullet(tf_s8, "Độ đo tính toán (Calculated)", "Định nghĩa Calculated Measures chuẩn xác:", 13)
    add_bullet(tf_s8, "", "• [Mean SCORE MARK] = Điểm TB\n• [Score 2025], [YoY Growth] = Tăng trưởng", 12, text_color=CYAN_ACCENT, prefix_color=CYAN_ACCENT)

    add_speaker_notes(s8, """[07:00 - 08:00] KHỐI PHÂN TÍCH OLAP SSAS:
Ở Chương III, nhóm triển khai khối dữ liệu đa chiều SSAS Multidimensional Cube:
Trong Data Source View, nhóm thiết lập các Hierarchy quan trọng như phân cấp Địa lý từ Tỉnh đến Trường, phân cấp Đào tạo từ Nhóm ngành xuống Ngành và Chương trình cụ thể.
Đặc biệt trong tab Dimension Usage, nhóm đã cấu hình thành công quan hệ Referenced Dimension cho DIM_MAJOR và Many-to-Many Dimension cho nhóm ngành và tổ hợp xét tuyển.
Nhờ đó, người dùng có thể cắt lát (Slice & Dice), xoay chiều (Pivot) và khoan sâu (Drill-down) dữ liệu theo mọi góc nhìn nghiệp vụ với tốc độ tính toán tức thì.""")

    # =========================================================================
    # SLIDE 9: KHAI THÁC ĐA CHIỀU VỚI MDX (CHƯƠNG 3)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Chương III: Truy Vấn Đa Chiều (MDX)", "Khai Thác Chuyên Sâu 15 Bài Toán Nghiệp Vụ Với MDX", 9)
    
    # Left: MDX Query Image (image239.png)
    img_mdx = os.path.join("key_images", "image239.png")
    if os.path.exists(img_mdx):
        s9.shapes.add_picture(img_mdx, Inches(0.7), Inches(1.5), Inches(5.8), Inches(5.2))
        
    # Right: Text Card
    _, tf_s9 = add_card(s9, 6.7, 1.5, 5.9, 5.2, "Tổng Hợp 15 Câu Truy Vấn Nghiệp Vụ", CYAN_ACCENT)
    add_bullet(tf_s9, "Độ phủ bài toán", "Nhóm đã hoàn thành xuất sắc 15 câu truy vấn MDX bao phủ mọi lát cắt phân tích nghiệp vụ.", 13)
    add_bullet(tf_s9, "Xếp hạng & Tối ưu (Top-N)", "Truy vấn 2 (TOP 10 ngành điểm cao nhất 2025: Y khoa, Răng Hàm Mặt, Khoa học máy tính, AI) & Truy vấn 4 (TOP 5 tổ hợp phổ biến nhóm CNTT: A00, A01, D01...).", 13)
    add_bullet(tf_s9, "Khoan sâu & So sánh không gian", "Truy vấn 3 (Drill-down Nhóm ngành -> Ngành), Truy vấn 5 (So sánh Điểm TB và Max giữa Hà Nội & TP.HCM).", 13)
    add_bullet(tf_s9, "Tăng trưởng theo thời gian (YoY)", "Truy vấn 11 (Tốc độ tăng trưởng điểm chuẩn nhóm Kinh tế qua các năm) & Truy vấn 13 (So sánh 5 tổ hợp truyền thống A00-D01 suốt 10 năm).", 13)
    add_bullet(tf_s9, "Truy vết biến động đột biến", "Truy vấn 15 (Truy vết các trường/ngành nhóm CNTT có điểm chuẩn năm 2025 tăng vọt >= 2.5 điểm so với năm 2024).", 13)

    add_speaker_notes(s9, """[08:00 - 09:00] TRUY VẤN ĐA CHIỀU VỚI MDX:
Trên nền tảng khối Cube, nhóm đã xây dựng và kiểm thử thành công 15 câu truy vấn MDX phân tích chuyên sâu được thể hiện qua cả Cube Browser và Excel Pivot Table.
Một số kết quả nghiệp vụ rất đáng chú ý:
- Truy vấn 2: Xác định top ngành có điểm chuẩn cao nhất toàn quốc luôn thuộc về Y khoa và Công nghệ thông tin/Trí tuệ nhân tạo.
- Truy vấn 5: Điểm chuẩn các trường tại Hà Nội và TP.HCM có sự phân hóa cao nhất cả nước.
- Truy vấn 15: Sử dụng hàm Filter kết hợp Calculated Member để tìm ra các trường khối CNTT có điểm chuẩn tăng đột biến từ 2.5 điểm trở lên, phản ánh xu hướng dịch chuyển nguyện vọng thực tế của thí sinh.""")

    # =========================================================================
    # SLIDE 10: TRỰC QUAN HÓA QUẢN TRỊ VỚI POWER BI (CHƯƠNG 4)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Chương IV: Báo Biểu Trực Quan (Power BI)", "3 Báo Cáo Phân Tích Chiến Lược Tuyển Sinh Trên Power BI", 10)
    
    # Left: Power BI Image (image35.png or image84.png)
    img_pbi = os.path.join("key_images", "image35.png")
    if os.path.exists(img_pbi):
        s10.shapes.add_picture(img_pbi, Inches(0.7), Inches(1.5), Inches(7.2), Inches(3.2))
        
    img_pbi2 = os.path.join("key_images", "image84.png")
    if os.path.exists(img_pbi2):
        s10.shapes.add_picture(img_pbi2, Inches(0.7), Inches(4.8), Inches(7.2), Inches(2.0))

    # Right: Text Card
    _, tf_s10 = add_card(s10, 8.1, 1.5, 4.5, 5.2, "Báo Cáo Trực Quan Power BI", AMBER_ACCENT)
    add_bullet(tf_s10, "Report 1: Xu hướng & Cơ cấu phương thức", "Theo dõi biến động điểm chuẩn qua từng năm kết hợp tỷ trọng các phương thức tuyển sinh (Line & Stacked Column). Thấy rõ sự chuyển dịch từ thi tốt nghiệp sang xét tuyển kết hợp.", 13)
    add_bullet(tf_s10, "Report 2: Cạnh tranh theo nhóm ngành", "Trực quan hóa mức độ cạnh tranh giữa các nhóm ngành đào tạo (Line and Clustered Column Chart). Bộc lộ khoảng cách điểm chuẩn giữa khối Kỹ thuật - Y dược với các ngành Khoa học xã hội.", 13)
    add_bullet(tf_s10, "Report 3: Đối sánh THPT vs Học bạ", "Sử dụng biểu đồ phân tán (Scatter Chart) so sánh trực tiếp điểm chuẩn thi tốt nghiệp THPT và xét học bạ cùng ngành cùng trường, giúp thí sinh nhận diện độ lệch tiêu chuẩn.", 13)

    add_speaker_notes(s10, """[09:00 - 10:00] BÁO BIỂU POWER BI:
Chuyển sang Chương IV - Trực quan hóa dữ liệu. Nhóm đã xây dựng 3 báo cáo dashboard chuyên nghiệp trên Microsoft Power BI:
- Báo cáo 1: Phản ánh xu hướng điểm chuẩn và cơ cấu các phương thức tuyển sinh qua 15 năm, cho thấy các phương thức mới đang ngày càng chiếm tỷ trọng lớn.
- Báo cáo 2: Đánh giá sức nóng và độ cạnh tranh của các nhóm ngành.
- Báo cáo 3: Đối sánh tương quan giữa điểm thi THPT và điểm học bạ thông qua Scatter plot, phát hiện hiện tượng lạm phát điểm học bạ ở một số cơ sở đào tạo.""")

    # =========================================================================
    # SLIDE 11: TRỰC QUAN HÓA GOOGLE LOOKER STUDIO (CHƯƠNG 4)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Chương IV: Báo Biểu Trực Quan (Looker Studio)", "Báo Biểu Phân Tích Không Gian Địa Lý & Biến Động Điểm Chuẩn", 11)
    
    # Left: Looker Studio Images (image395.png & image199.png)
    img_looker1 = os.path.join("key_images", "image395.png")
    if os.path.exists(img_looker1):
        s11.shapes.add_picture(img_looker1, Inches(0.7), Inches(1.5), Inches(7.2), Inches(3.2))
        
    img_looker2 = os.path.join("key_images", "image199.png")
    if os.path.exists(img_looker2):
        s11.shapes.add_picture(img_looker2, Inches(0.7), Inches(4.8), Inches(7.2), Inches(2.0))

    # Right: Text Card
    _, tf_s11 = add_card(s11, 8.1, 1.5, 4.5, 5.2, "Báo Cáo Trên Looker Studio", GREEN_ACCENT)
    add_bullet(tf_s11, "Report 1: Bản đồ không gian địa lý", "Khai thác dữ liệu Geo-spatial với bản đồ nhiệt Việt Nam. Thể hiện mật độ và mức điểm chuẩn trung bình tập trung cao tại 2 trung tâm giáo dục lớn: Hà Nội và TP.HCM, lan tỏa ra Đà Nẵng, Cần Thơ.", 13)
    add_bullet(tf_s11, "Report 2: Biến động điểm chuẩn 2024 - 2025", "Tính toán Delta Score = Score_2025 - Score_2024. Nhận diện các ngành có điểm chuẩn tăng đột biến hoặc sụt giảm mạnh, cung cấp bức tranh dao động tức thời cho thí sinh năm kế tiếp.", 13)
    add_bullet(tf_s11, "Report 3: Tổ hợp môn phổ biến", "Thống kê ma trận tổ hợp xét tuyển cho từng nhóm ngành, giúp học sinh THPT định hướng tổ hợp ôn tập trọng tâm.", 13)

    add_speaker_notes(s11, """[10:00 - 11:00] BÁO BIỂU LOOKER STUDIO:
Bên cạnh Power BI, nhóm mở rộng triển khai trên Google Looker Studio để tận dụng thế mạnh phân tích dữ liệu không gian địa lý và chia sẻ web linh hoạt:
- Report 1 là Bản đồ nhiệt (Geo Map) định vị toàn bộ các trường đại học tại 63 tỉnh thành.
- Report 2 phân tích độ lệch Delta Score giữa 2 năm gần nhất 2024 và 2025, giúp cảnh báo các ngành đang có xu hướng tăng nhiệt đột biến.
- Report 3 cung cấp ma trận phân bổ tổ hợp môn giúp định hướng nghề nghiệp sớm cho học sinh bậc THPT.""")

    # =========================================================================
    # SLIDE 12: KHAI PHÁ DỮ LIỆU - BÀI TOÁN & PIPELINE (CHƯƠNG 5)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Chương V: Khai Phá Dữ Liệu (Data Mining)", "Định Hình Bài Toán Học Máy & Pipeline Tiền Xử Lý Đặc Trưng", 12)
    
    # 2 Cards: Left: Bài toán & Split; Right: Pipeline Features
    _, tf_s12_l = add_card(s12, 0.7, 1.5, 5.8, 5.2, "Định Hình Bài Toán & Chia Dữ Liệu", CYAN_ACCENT)
    add_bullet(tf_s12_l, "Bài toán phân loại đa lớp", "Dự đoán phân khúc điểm chuẩn (Multi-class Classification) cho phương thức Điểm thi THPT:", 13.5)
    add_bullet(tf_s12_l, "", "• Nhóm 1: Dưới 18 điểm (Mức an toàn / xét tuyển dễ)\n• Nhóm 2: Từ 18 đến dưới 22 điểm (Mức trung bình khá)\n• Nhóm 3: Từ 22 đến dưới 25 điểm (Mức cạnh tranh cao)\n• Nhóm 4: Từ 25 điểm trở lên (Mức xuất sắc / Top đầu)", 12.5, text_color=AMBER_ACCENT, prefix_color=AMBER_ACCENT)
    add_bullet(tf_s12_l, "Phân chia theo dòng thời gian", "Mô phỏng bài toán thực tế, ngăn ngừa triệt để rò rỉ dữ liệu tương lai (Data Leakage):", 13.5)
    add_bullet(tf_s12_l, "", "• Train (<= 2023): 37,666 dòng (74.08%)\n• Validation (2024): 5,658 dòng (11.13%)\n• Test Độc Lập (2025): 7,519 dòng (14.79%)", 12.5, text_color=GREEN_ACCENT, prefix_color=GREEN_ACCENT)

    _, tf_s12_r = add_card(s12, 6.8, 1.5, 5.8, 5.2, "Pipeline Tiền Xử Lý Scikit-Learn", PURPLE_ACCENT)
    add_bullet(tf_s12_r, "Thiết kế ColumnTransformer", "Xây dựng pipeline chuyển đổi đồng bộ cho cả tập Train, Val và Test độc lập.", 13.5)
    add_bullet(tf_s12_r, "6 Đặc trưng danh mục (Categorical)", "school_id, school_type, province_name, program_name, major_groups, block_set.", 13.5)
    add_bullet(tf_s12_r, "", "• Xử lý thiếu: SimpleImputer nhãn 'Chưa xác định'.\n• Mã hóa: OrdinalEncoder với unknown_value=-1 tự động nhận diện các trường/ngành mới xuất hiện trong tập Test.", 12.5, text_color=CYAN_ACCENT, prefix_color=CYAN_ACCENT)
    add_bullet(tf_s12_r, "3 Đặc trưng số học & Độ trễ (Lag)", "score_year, previous_year_score (điểm năm trước), has_previous_year_score.", 13.5)
    add_bullet(tf_s12_r, "", "• Điền giá trị khuyết các ngành mới mở bằng trung vị median (SimpleImputer).", 12.5, text_color=TEXT_MUTED, prefix_color=TEXT_MUTED)

    add_speaker_notes(s12, """[11:00 - 12:00] KHAI PHÁ DỮ LIỆU - PIPELINE:
Đến với Chương V - điểm nhấn nghiên cứu nâng cao của đồ án: Nhóm ứng dụng Học máy để giải quyết bài toán dự đoán phân khúc điểm chuẩn tuyển sinh thành 4 nhóm cạnh tranh.
Nhóm áp dụng nguyên tắc Time-series Split nghiêm ngặt: Tập huấn luyện lấy toàn bộ dữ liệu từ 2023 trở về trước, Validation là năm 2024 và Test hoàn toàn độc lập là năm 2025.
Pipeline tiền xử lý được thiết kế chuyên nghiệp qua ColumnTransformer: mã hóa biến phân loại bằng OrdinalEncoder xử lý được cả các ngành/trường mới xuất hiện ở tập kiểm thử, và tạo đặc trưng độ trễ lag feature là điểm chuẩn năm trước liền kề.""")

    # =========================================================================
    # SLIDE 13: ĐÁNH GIÁ & SO SÁNH 4 MÔ HÌNH HỌC MÁY (CHƯƠNG 5)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "Chương V: Khai Phá Dữ Liệu (Data Mining)", "Đánh Giá Hiệu Năng 4 Thuật Toán & Tầm Ảnh Hưởng Đặc Trưng", 13)
    
    # Left: Comparison Barplot Image (image333.png)
    img_ml = os.path.join("key_images", "image333.png")
    if os.path.exists(img_ml):
        s13.shapes.add_picture(img_ml, Inches(0.7), Inches(1.5), Inches(5.8), Inches(5.2))
        
    # Right: Text Card with Model Metrics & Insights
    _, tf_s13 = add_card(s13, 6.7, 1.5, 5.9, 5.2, "So Sánh Hiệu Năng Mô Hình (Test 2025)", GREEN_ACCENT)
    add_bullet(tf_s13, "Baseline Ngẫu Nhiên", "Độ chính xác chuẩn xác suất lớp đa số: ~31.48%. Tất cả mô hình đều vượt trội mốc này.", 13)
    add_bullet(tf_s13, "Decision Tree (Cây đơn lẻ)", "Accuracy: 39.86%  |  F1-Score: 37.95% (Dễ bị phân mảnh dữ liệu, độ chính xác cơ bản).", 13)
    add_bullet(tf_s13, "XGBoost (Boosting mạnh mẽ)", "Accuracy: 51.55%  |  F1-Score: 48.13% (Bước nhảy vọt đáng kể nhờ tối ưu hàm mất mát bậc 2).", 13)
    add_bullet(tf_s13, "LightGBM (Quán Quân Xuất Sắc)", "Accuracy: 54.99%  |  F1-Score: 51.09% (Hiệu năng dẫn đầu, tối ưu hóa phân nhóm dữ liệu dạng bảng cực tốt).", 13.5, text_color=TEXT_WHITE, prefix_color=GREEN_ACCENT)
    add_bullet(tf_s13, "Stacking Classifier", "Accuracy: 44.35%  |  F1-Score: 44.22% (Kết hợp đa mô hình nhưng tăng chi phí tính toán mà không cải thiện thêm).", 13)
    add_bullet(tf_s13, "Permutation Feature Importance", "Điểm chuẩn năm trước (previous_year_score) và Nhóm ngành (major_groups) là 2 đặc trưng chi phối mạnh nhất đến kết quả dự đoán.", 13)

    add_speaker_notes(s13, """[12:00 - 13:00] KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH:
Trên tập kiểm thử độc lập năm 2025:
- Baseline ngẫu nhiên là 31.48%.
- Decision Tree đạt Accuracy 39.86%.
- XGBoost tạo bước nhảy vọt lên 51.55%.
- Và LightGBM đã xuất sắc giành vị trí Quán quân với Accuracy đạt xấp xỉ 55% và F1-Score đạt 51.09%.
Mặc dù nhóm đã thử nghiệm mô hình Stacking Classifier phân tầng, nhưng hiệu năng chỉ đạt 44.35% và làm tăng đáng kể độ trễ tính toán. Do đó, LightGBM là mô hình tối ưu nhất được lựa chọn.
Phân tích Permutation Importance cũng chỉ ra: Điểm chuẩn năm trước và Nhóm ngành là 2 nhân tố quan trọng nhất quyết định điểm trúng tuyển của một ngành đào tạo.""")

    # =========================================================================
    # SLIDE 14: TỔNG KẾT THÀNH QUẢ & ĐÓNG GÓP CỦA ĐỀ TÀI
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "Tổng Kết Đồ Án", "Các Thành Quả Chính & Giá Trị Thực Tiễn Đạt Được", 14)
    
    # 4 Achievement Cards in 2x2 grid
    c_w = 5.8
    c_h = 2.45
    
    _, tf_a1 = add_card(s14, 0.7, 1.55, c_w, c_h, "1. Kho DWH Chuẩn Hóa Hoàn Chỉnh", CYAN_ACCENT)
    add_bullet(tf_a1, "Snowflake Schema 3NF", "Thiết kế thành công kho dữ liệu 13 bảng trên SQL Server, giải quyết trọn vẹn quan hệ Nhiều - Nhiều qua 3 bảng Bridge.", 13)
    add_bullet(tf_a1, "Dữ liệu sạch quy mô lớn", "Hơn 103,000 bản ghi được làm sạch, đồng nhất thang điểm 30, loại bỏ lỗi nhập liệu và ngoại lai.", 13)

    _, tf_a2 = add_card(s14, 6.8, 1.55, c_w, c_h, "2. Tự Động Hóa ETL & Khối SSAS Cube", AMBER_ACCENT)
    add_bullet(tf_a2, "SSIS Package tự động", "Quy trình Control Flow nạp dữ liệu tuần tự, an toàn khóa ngoại với Precedence Constraints.", 13)
    add_bullet(tf_a2, "Khối OLAP tốc độ cao", "Xây dựng Cube SSAS hoàn chỉnh với phân cấp Hierarchies và Calculated Measures, giải quyết 15 truy vấn MDX nghiệp vụ phức tạp.", 13)

    _, tf_a3 = add_card(s14, 0.7, 4.25, c_w, c_h, "3. Báo Biểu Quản Trị Trực Quan Đa Nền Tảng", GREEN_ACCENT)
    add_bullet(tf_a3, "Hệ thống 6 Dashboards", "Triển khai đồng thời trên Power BI (xu hướng, cạnh tranh, đối sánh học bạ) và Google Looker Studio (bản đồ địa lý, delta score).", 13)
    add_bullet(tf_a3, "Hỗ trợ đa đối tượng", "Phục vụ thiết thực cho thí sinh chọn trường, nhà trường tuyển sinh và cơ quan quản lý.", 13)

    _, tf_a4 = add_card(s14, 6.8, 4.25, c_w, c_h, "4. Khai Phá Dữ Liệu Thông Minh", PURPLE_ACCENT)
    add_bullet(tf_a4, "Mô hình LightGBM tối ưu", "Đạt Accuracy 54.99% trên tập kiểm thử 2025 hoàn toàn độc lập, vượt xa baseline.", 13)
    add_bullet(tf_a4, "Pipeline có khả năng mở rộng", "Dễ dàng tích hợp vào hệ thống gợi ý nguyện vọng thông minh cho các kỳ tuyển sinh tiếp theo.", 13)

    add_speaker_notes(s14, """[13:00 - 14:00] TỔNG KẾT ĐÓNG GÓP:
Tóm lại, qua đề tài này, nhóm sinh viên chúng em đã giải quyết trọn vẹn một chu trình BI và Data Warehouse chuẩn công nghiệp:
1. Xây dựng Kho dữ liệu bông tuyết sạch sẽ, xử lý triệt để bài toán quan hệ nhiều-nhiều.
2. Tự động hóa toàn diện quy trình tích hợp SSIS và khối SSAS Cube với 15 truy vấn MDX chuyên sâu.
3. Cung cấp 6 Dashboard trực quan hóa trực quan trên cả Power BI và Looker Studio.
4. Mở rộng thành công bài toán Khai phá dữ liệu với mô hình LightGBM có độ tin cậy cao trên tập kiểm thử 2025.""")

    # =========================================================================
    # SLIDE 15: ĐỊNH HƯỚNG PHÁT TRIỂN & Q&A
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)
    add_header(s15, "Định Hướng & Thảo Luận", "Hướng Mở Rộng Đề Tài & Phiên Hỏi Đáp (Q&A)", 15)
    
    # Left: Future Work
    _, tf_f1 = add_card(s15, 0.7, 1.55, 5.8, 5.15, "Định Hướng Phát Triển Tương Lai", CYAN_ACCENT)
    add_bullet(tf_f1, "Mở rộng nguồn dữ liệu", "Tích hợp thêm dữ liệu chỉ tiêu tuyển sinh theo phương thức, phổ điểm thi THPT toàn quốc hàng năm và dữ liệu việc làm sinh viên tốt nghiệp.", 13.5)
    add_bullet(tf_f1, "Nâng cấp kiến trúc dữ liệu", "Triển khai hồ dữ liệu (Data Lakehouse) trên nền tảng đám mây (Azure Synapse / Databricks) để đáp ứng dữ liệu lớn thời gian thực.", 13.5)
    add_bullet(tf_f1, "Xây dựng Web Application", "Đóng gói mô hình Machine Learning LightGBM thành API và giao diện Web/Mobile hỗ trợ thí sinh nhập điểm thi để tự động gợi ý danh sách nguyện vọng tối ưu theo thuật toán xếp hạng.", 13.5)

    # Right: Thank you & Q&A Card
    _, tf_f2 = add_card(s15, 6.8, 1.55, 5.8, 5.15, "Lời Cảm Ơn & Phiên Thảo Luận (Q&A)", AMBER_ACCENT)
    add_bullet(tf_f2, "Lời cảm ơn chân thành", "Nhóm xin chân thành cảm ơn ThS. Đỗ Thị Minh Phụng đã tận tình hướng dẫn, chỉ bảo chuyên môn sâu sắc trong suốt quá trình thực hiện đồ án.", 14)
    add_bullet(tf_f2, "Cảm ơn Hội đồng đánh giá", "Cảm ơn quý Thầy Cô trong Hội đồng đã lắng nghe bài báo cáo của nhóm.", 14)
    
    # Big Q&A Box inside right card
    qa_box = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(4.3), Inches(5.0), Inches(2.0))
    qa_box.fill.solid()
    qa_box.fill.fore_color.rgb = CARD_BG_LIGHT
    qa_box.line.color.rgb = GREEN_ACCENT
    qa_box.line.width = Pt(1.5)
    tf_qa = qa_box.text_frame
    tf_qa.word_wrap = True
    tf_qa.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_qa1 = tf_qa.paragraphs[0]
    p_qa1.text = "XIN TRÂN TRỌNG CẢM ƠN!"
    p_qa1.font.name = "Segoe UI"
    p_qa1.font.size = Pt(20)
    p_qa1.font.bold = True
    p_qa1.font.color.rgb = GREEN_ACCENT
    p_qa1.alignment = PP_ALIGN.CENTER
    
    p_qa2 = tf_qa.add_paragraph()
    p_qa2.text = "Nhóm rất mong nhận được câu hỏi & góp ý từ Quý Thầy Cô!"
    p_qa2.font.name = "Segoe UI"
    p_qa2.font.size = Pt(13)
    p_qa2.font.color.rgb = TEXT_LIGHT
    p_qa2.alignment = PP_ALIGN.CENTER

    add_speaker_notes(s15, """[14:00 - 15:00] ĐỊNH HƯỚNG TƯƠNG LAI & KẾT THÚC:
Về hướng phát triển tiếp theo, nhóm dự kiến mở rộng tích hợp phổ điểm thi THPT quốc gia và xây dựng một Web App tư vấn nguyện vọng tự động bằng AI dựa trên mô hình LightGBM đã huấn luyện.
Một lần nữa, chúng em xin chân thành cảm ơn Cô Đỗ Thị Minh Phụng cùng quý Thầy Cô trong Hội đồng đã lắng nghe.
Sau đây, nhóm chúng em xin sẵn sàng lắng nghe các câu hỏi và đóng góp ý kiến từ quý Thầy Cô. Em xin chân thành cảm ơn!""")

    output_path = r"d:\UNIDOCS\IS217.R11-OLAP\Slide_ThuyetTrinh_OLAP_TuyenSinh_15Phut.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_presentation()
