-- ============================================================================
--  IlFreight Logistics — Lab SQLi  |  init.sql
--  Tao 2 database: ilfreight (app chinh) + dev (muc tieu enumeration)
--  Seed du lieu that + flags theo tung ky thuat khai thac.
-- ============================================================================

-- ------------------------------------------------------------------
--  Privilege: root duoc phep ket noi tu moi host, co FILE privilege
--  (FILE la mac dinh cua root; ta khang dinh lai cho ro rang).
-- ------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
GRANT FILE ON *.* TO 'root'@'%';
FLUSH PRIVILEGES;

-- ============================================================================
--  DATABASE: ilfreight  (web app chay o day)
-- ============================================================================
CREATE DATABASE IF NOT EXISTS ilfreight CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ilfreight;

-- ---- users ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id             INT NOT NULL AUTO_INCREMENT,
    username       VARCHAR(100) UNIQUE NOT NULL,
    password       VARCHAR(255) NOT NULL,   -- luu cleartext (bad practice CO Y)
    email          VARCHAR(150),
    role           VARCHAR(20) DEFAULT 'customer',
    api_key        VARCHAR(64),
    remember_token VARCHAR(64),
    PRIMARY KEY (id)
);

INSERT INTO users (username, password, email, role, api_key) VALUES
('admin',   'p@ssw0rd',    'admin@ilfreight.local',  'admin',    'ILF-ADM-9f3c1a77e2b04d55'),
('jsmith',  'Spring2024!', 'jsmith@ilfreight.local', 'customer', 'ILF-CUS-1b2c3d4e5f60718'),
('awong',   'Hongkong88',  'awong@ilfreight.local',  'customer', 'ILF-CUS-aa11bb22cc33dd44'),
('mgarcia', 'Barca#2010',  'mgarcia@ilfreight.local','staff',    'ILF-STF-99887766554433');

-- ---- ports (bang tra cuu cong khai — giong bai giang) ----------------------
CREATE TABLE IF NOT EXISTS ports (
    id      INT NOT NULL AUTO_INCREMENT,
    code    VARCHAR(10),
    city    VARCHAR(100),
    country VARCHAR(100),
    volume  DECIMAL(6,2),
    PRIMARY KEY (id)
);

INSERT INTO ports (code, city, country, volume) VALUES
('CN SHA', 'Shanghai',  'China',        37.13),
('SG SIN', 'Singapore', 'Singapore',    36.60),
('CN SHE', 'Shenzhen',  'China',        23.97),
('CN NGB', 'Ningbo',    'China',        27.53),
('AE DXB', 'Dubai',     'UAE',          15.73),
('BR SSZ', 'Santos',    'Brazil',        3.60),
('NL RTM', 'Rotterdam', 'Netherlands',  14.35),
('US LAX', 'Los Angeles','USA',          9.20);

-- ---- shipments (van don) ---------------------------------------------------
CREATE TABLE IF NOT EXISTS shipments (
    id          INT NOT NULL AUTO_INCREMENT,
    tracking_no VARCHAR(30) UNIQUE,
    port_code   VARCHAR(10),
    status      VARCHAR(40),
    customer_id INT,
    PRIMARY KEY (id)
);

INSERT INTO shipments (tracking_no, port_code, status, customer_id) VALUES
('ILF1042CN', 'CN SHA', 'In Transit',     2),
('ILF1043SG', 'SG SIN', 'At Port',        2),
('ILF1044AE', 'AE DXB', 'Customs Hold',   3),
('ILF1045NL', 'NL RTM', 'Delivered',      3),
('ILF1046US', 'US LAX', 'Out for Delivery',4);

-- ---- comments (binh luan don hang) ----------------------------------------
CREATE TABLE IF NOT EXISTS comments (
    id          INT NOT NULL AUTO_INCREMENT,
    shipment_id INT,
    user_id     INT,
    content     TEXT,
    created_at  DATETIME DEFAULT NOW(),
    PRIMARY KEY (id)
);

INSERT INTO comments (shipment_id, user_id, content) VALUES
(1, 2, 'Xin cho biet ngay du kien cap cang?'),
(1, 4, 'Du kien cap cang Shanghai trong 3 ngay toi.'),
(3, 3, 'Hang bi giu o hai quan, can ho tro gap.');

-- ---- news ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS news (
    id           INT NOT NULL AUTO_INCREMENT,
    title        VARCHAR(200),
    body         TEXT,
    published_at DATETIME DEFAULT NOW(),
    PRIMARY KEY (id)
);

INSERT INTO news (title, body, published_at) VALUES
('Mở rộng tuyến vận tải biển trực tiếp Thượng Hải – Rotterdam (Shanghai – Rotterdam)', 'IlFreight Logistics chính thức đưa vào khai thác tuyến vận tải container định tuyến hàng tuần kết nối trực tiếp khu vực Đông Á với cụm cảng cửa ngõ Tây Âu, đi qua Thượng Hải (CN SHA), Ninh Ba (CN NGB), Singapore (SG SIN) và cập cảng Rotterdam (NL RTM).\n\nTuyến vận tải mới giúp rút ngắn thời gian hải trình trung bình xuống còn 26 ngày, giảm thiểu khâu chuyển tải trung gian và tăng thêm 35% năng lực cấp vỏ container 40GP/40HC trong giai đoạn cao điểm xuất khẩu cuối năm.\n\nKhách hàng xuất khẩu nhóm hàng linh kiện điện tử, máy móc cơ khí và nông sản chế biến sâu có thể đặt chỗ trực tiếp qua cổng Booking trực tuyến của IlFreight với chính sách cam kết giữ tải (Space Guarantee) và hỗ trợ làm thủ tục hải quan trọn gói tại cả hai đầu cảng.', '2026-11-08 09:00:00'),
('Nâng cấp hệ thống tra cứu vận đơn và cảnh báo hành trình thời gian thực', 'Nền tảng IlFreight Digital Portal phiên bản mới vừa hoàn tất nâng cấp đồng bộ dữ liệu AIS từ hơn 120 thương cảng trọng điểm, cho phép doanh nghiệp chủ hàng theo dõi từng cột mốc hành trình từ lúc tiếp nhận booking (Booked), đang hải trình (In Transit), cập cảng (At Port) cho tới khi thông quan và giao hàng (Delivered).\n\nĐiểm nhấn của bản nâng cấp lần này là hệ thống cảnh báo tức thời ngay trên giao diện người dùng mỗi khi lô hàng thay đổi trạng thái hoặc phát sinh kiểm hoá hải quan (Customs Hold), kèm khả năng xuất nhanh Vận đơn đường biển (B/L) và Hoá đơn thương mại điện tử sẵn sàng in ấn.\n\nNgoài ra, khách hàng có thể trao đổi trực tiếp với nhân viên chứng từ tại trang chi tiết vận đơn để rút ngắn thời gian xử lý hồ sơ xuất nhập khẩu.', '2026-11-05 14:30:00'),
('Xuất nhập khẩu Việt Nam vượt mốc 1.000 tỷ USD năm 2026: Cơ hội và bài toán tối ưu chi phí Logistics', 'Theo số liệu tổng hợp thị trường thương mại 10 tháng năm 2026, tổng kim ngạch xuất nhập khẩu hàng hoá của Việt Nam lần đầu tiên vượt cột mốc lịch sử 1.000 tỷ USD (đạt trên 1.010 tỷ USD, tăng trưởng hơn 32% so với cùng kỳ). Đà tăng trưởng kỷ lục đến từ các ngành hàng chủ lực như điện tử, linh kiện bán dẫn, dệt may, giày dép và nông sản chế biến.\n\nTuy nhiên, áp lực lên hệ thống logistics quốc gia vẫn còn rất lớn khi chi phí logistics bình quân tại Việt Nam hiện dao động ở mức 16–17% GDP, cao hơn mức trung bình thế giới (10–12%). Việc giải quyết các điểm nghẽn kết nối giữa khu công nghiệp nội địa và cụm cảng nước sâu đang trở thành ưu tiên cấp thiết.\n\nTriển khai Chiến lược phát triển dịch vụ logistics Việt Nam thời kỳ 2025–2035, tầm nhìn đến năm 2050 (Quyết định số 2229/QĐ-TTg), ngành vận tải đặt mục tiêu kéo giảm tỷ lệ chi phí logistics xuống còn 12–15% GDP thông qua số hoá chứng từ hải quan và phát triển các trung tâm logistics quy mô vùng.', '2026-11-02 10:15:00'),
('Ba cảng biển Việt Nam góp mặt trong Top 100 cảng container lớn nhất thế giới theo Lloyd’s List 2026', 'Bảng xếp hạng thường niên năm 2026 do tạp chí hàng hải uy tín Lloyd’s List (Vương quốc Anh) công bố tiếp tục ghi nhận 3 cụm cảng cửa ngõ của Việt Nam trong Top 100 cảng container có sản lượng thông qua cao nhất toàn cầu.\n\nCụ thể, cụm cảng TP. Hồ Chí Minh giữ vững vị trí thứ 22 thế giới; cảng Hải Phòng bứt phá tăng 3 bậc lên vị trí thứ 26 nhờ sản lượng tăng mạnh từ các bến container nước sâu khu vực Lạch Huyện; trong khi cụm cảng nước sâu Cái Mép – Thị Vải đứng ở vị trí thứ 31, giữ vai trò điểm đón trực tiếp các tàu mẹ siêu lớn chạy tuyến thẳng châu Âu và Bờ Tây Bắc Mỹ.\n\nKết quả này khẳng định năng lực trung chuyển và sức hấp dẫn ngày càng tăng của hệ thống cảng biển Việt Nam trong bản đồ chuỗi cung ứng khu vực châu Á – Thái Bình Dương.', '2026-10-29 08:45:00'),
('Diễn đàn Logistics Việt Nam 2026: Thúc đẩy vận tải ven biển và chuỗi cung ứng lạnh liên vùng', 'Đầu tháng 11/2026, Diễn đàn Logistics Việt Nam 2026 với chủ đề "Kết nối logistics cao nguyên, vươn ra chuỗi cung ứng toàn cầu" đã tập trung thảo luận các giải pháp tháo gỡ nút thắt hạ tầng vận chuyển cho khu vực miền Trung – Tây Nguyên.\n\nDo địa hình chia cắt và phụ thuộc lớn vào vận tải đường bộ dọc Quốc lộ 19 kết nối tới cảng Quy Nhơn, các chuyên gia hàng hải đã đề xuất phát triển mạnh đội tàu vận tải ven biển quy mô 300–600 TEU kết hợp hệ thống kho lạnh trung chuyển tại cảng.\n\nMô hình kết hợp giữa kho lạnh tiêu chuẩn quốc tế và vận tải thuỷ nội địa – ven biển giúp doanh nghiệp xuất khẩu cà phê, sầu riêng, hồ tiêu và cao su tiết kiệm 15–22% cước vận chuyển, đồng thời giảm phát thải carbon so với phương thức chở container đường dài bằng xe đầu kéo.', '2026-10-24 16:00:00'),
('Vận tải biển xanh và lộ trình Net Zero: Xu hướng nhiên liệu LNG, Methanol xanh và chuẩn EU ETS', 'Các quy định mới về kiểm soát phát thải khí nhà kính từ Tổ chức Hàng hải Quốc tế (IMO) cùng cơ chế định giá carbon EU ETS đối với tàu cập cảng châu Âu đang tái định hình tiêu chuẩn khai thác đội tàu container quốc tế trong giai đoạn 2025–2026.\n\nNhiều hãng tàu lớn đã tăng tốc đầu tư đội tàu chạy nhiên liệu kép (Dual-fuel LNG, Methanol xanh và Amoniac xanh), song song với việc tối ưu hoá tốc độ hành trình (slow-steaming) và cắt giảm tình trạng container chạy rỗng quay đầu.\n\nIlFreight Logistics hiện đã tích hợp bảng ước tính phát thải CO2 theo từng tuyến vận tải và loại container (20GP, 40GP, 40HC), hỗ trợ các doanh nghiệp xuất khẩu sang thị trường EU và Hoa Kỳ đáp ứng yêu cầu báo cáo phát triển bền vững (ESG) của đối tác nhập khẩu.', '2026-10-18 11:20:00'),
('Mở rộng khu bến nước sâu Lạch Huyện và hợp tác phát triển trung tâm logistics kết nối đường sắt', 'Tại khu vực phía Bắc, loạt bến container nước sâu số 3, 4, 5 và 6 tại Lạch Huyện (Hải Phòng) lần lượt hoàn thiện và đưa vào vận hành trong giai đoạn 2025–2026, nâng cao năng lực tiếp nhận tàu container sức chở lên tới 18.000 TEU phục vụ các tuyến hải trình viễn dương không cần qua trung chuyển.\n\nBên cạnh hạ tầng cầu bến, xu hướng liên kết chiến lược giữa doanh nghiệp cảng biển trong nước và các tập đoàn khai thác cảng toàn cầu như APM Terminals (Maersk) đang đẩy mạnh hình thành các tổ hợp logistics hậu phương kết nối trực tiếp ga đường sắt hàng hoá.\n\nSự kết nối đa phương thức giữa tàu biển – đường sắt – đường bộ giúp rút ngắn thời gian giải phóng hàng tại bãi cảng và tăng tính ổn định cho các khu công nghiệp sản xuất điện tử ở Bắc Ninh, Thái Nguyên và Hải Dương.', '2026-10-12 09:30:00'),
('Ứng dụng AI và Bản sao số (Digital Twin) trong điều phối bãi container và dự báo tắc nghẽn cảng', 'Chuyển đổi số đang trở thành đòn bẩy cạnh tranh cốt lõi tại các thương cảng lớn như Thượng Hải (CN SHA), Singapore (SG SIN) và Rotterdam (NL RTM). Công nghệ Trí tuệ nhân tạo (AI) kết hợp mô hình Bản sao số (Digital Twin) cho phép mô phỏng luồng tàu ra vào luồng lạch và phân bổ vị trí xếp dỡ container hoàn toàn tự động.\n\nNhờ thuật toán dự báo thời gian tàu đến thực tế (Predictive ETA) và điều phối cổng thông minh (Smart Gate), thời gian xe đầu kéo chờ nhận container tại cảng đã giảm hơn 30% so với phương pháp thủ công.\n\nKết hợp với khai báo hải quan điện tử trước khi tàu cập cảng qua hệ thống VNACCS, các lô hàng của khách hàng tại IlFreight có thể thông quan nhanh chóng ngay trong 24 giờ sau khi dỡ hàng khỏi tàu.', '2026-10-05 15:10:00'),
('Lưu ý quy chuẩn đóng gói hàng nguy hiểm IMO IMDG và kiểm soát chuỗi lạnh xuất khẩu cuối năm', 'Bước vào quý IV, lưu lượng vận chuyển hàng hoá chất công nghiệp, pin lithium và thực phẩm đông lạnh qua các tuyến Singapore, Dubai Jebel Ali (AE DXB) và Los Angeles (US LAX) tăng mạnh. Để tránh rủi ro lô hàng bị tạm giữ kiểm hoá tại cảng chuyển tải (Customs Hold), chủ hàng cần tuân thủ nghiêm ngặt Bộ luật Hàng hải Quốc tế về Hàng nguy hiểm (IMDG Code).\n\nMọi lô hàng thuộc nhóm nguy hiểm phải cung cấp đầy đủ Phiếu an toàn hoá chất (MSDS) phiên bản cập nhật, sử dụng bao bì đạt chuẩn kiểm định UN và dán nhãn phân loại nguy hiểm đúng kích thước quy định trên cả 4 mặt container.\n\nĐối với container lạnh (Reefer Cargo), IlFreight khuyến nghị khách hàng kiểm tra trước dải nhiệt độ cài đặt (-18°C đến +4°C), độ mở thông gió (Ventilation) và lịch chạy máy phát điện dự phòng trước giờ cắt máng (Closing Time) tối thiểu 24 giờ.', '2026-09-26 10:00:00'),
('Biến động giá cước container Á – Âu và Bắc Mỹ quý IV/2026: Khuyến nghị đặt chỗ sớm cho doanh nghiệp', 'Thị trường vận tải container quốc tế trên trục Á – Âu (CN SHA / CN NGB – NL RTM) và xuyên Thái Bình Dương (CN SHA / SG SIN – US LAX) ghi nhận xu hướng điều chỉnh giá cước theo mùa cao điểm sản xuất phục vụ lễ hội cuối năm.\n\nNhu cầu đối với container 40GP và 40HC tăng 18–25%, khiến tỷ lệ lấp đầy tàu (Load Factor) trên nhiều tuyến chính duy trì ở mức trên 92%. Một số hãng tàu áp dụng điều chỉnh lịch trình hoặc phụ phí mùa cao điểm (PSS) đối với các đơn đặt chỗ cận ngày khởi hành.\n\nĐể chủ động ngân sách, IlFreight khuyến nghị doanh nghiệp sử dụng công cụ Dự toán Cước Vận Tải (/quote) để đối chiếu mức cước cơ bản và chốt lệnh đặt chỗ (Booking) trước ETD ít nhất 10–14 ngày.', '2026-09-15 08:30:00'),
('Hướng dẫn lựa chọn điều kiện Incoterms 2020 (FOB, CIF, DDP) tối ưu khi xuất khẩu đường biển', 'Việc lựa chọn điều kiện thương mại quốc tế Incoterms 2020 ảnh hưởng trực tiếp tới điểm chuyển giao rủi ro, quyền thuê tàu và trách nhiệm mua bảo hiểm hàng hoá giữa người bán và người mua.\n\nVới điều kiện FOB (Free On Board), trách nhiệm và rủi ro của người bán kết thúc ngay khi hàng hoá được xếp an toàn qua lan can lên boong tàu tại cảng bốc, phù hợp khi bên mua nắm ưu thế về hợp đồng cước với hãng tàu.\n\nTrong khi đó, điều kiện CIF (Cost, Insurance and Freight) cho phép doanh nghiệp xuất khẩu chủ động lựa chọn đơn vị giao nhận uy tín và mua bảo hiểm hàng hải tối thiểu 110% giá trị hoá đơn, còn DDP (Delivered Duty Paid) giúp mở rộng khả năng giao trọn gói tận kho người mua. Quý khách có thể tra cứu bảng đối chiếu đầy đủ 11 quy tắc Incoterms 2020 tại mục Quy chuẩn & Biểu mẫu (/guide).', '2026-09-03 13:45:00');

-- ----------------------------------------------------------------------------
-- BANG NGHIEP VU MO RONG (Business Features)
-- ----------------------------------------------------------------------------

-- ---- user_profiles ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id          INT NOT NULL,
    full_name        VARCHAR(100),
    phone            VARCHAR(20),
    company          VARCHAR(100),
    address          VARCHAR(255),
    is_locked        TINYINT DEFAULT 0,
    accepted_terms_at DATETIME,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    CONSTRAINT fk_user_profiles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO user_profiles (user_id, full_name, phone, company, address, is_locked, accepted_terms_at) VALUES
(1, 'Admin IlFreight', '0901234567', 'IlFreight HQ', 'Hai Phong, Vietnam', 0, NOW()),
(2, 'John Smith', '+1-555-0199', 'Smith Trading Co.', 'Los Angeles, USA', 0, NOW()),
(3, 'Alice Wong', '+852-9123-4567', 'Wong Import Export Ltd.', 'Hong Kong', 0, NOW()),
(4, 'Maria Garcia', '+34-600-112233', 'Garcia Logistics S.L.', 'Barcelona, Spain', 0, NOW());

-- ---- password_resets -------------------------------------------------------
CREATE TABLE IF NOT EXISTS password_resets (
    id         INT NOT NULL AUTO_INCREMENT,
    user_id    INT NOT NULL,
    token_hash CHAR(64) UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at    DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_password_resets_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---- shipment_details ------------------------------------------------------
CREATE TABLE IF NOT EXISTS shipment_details (
    shipment_id       INT NOT NULL,
    shipper_name      VARCHAR(100),
    shipper_address   VARCHAR(255),
    consignee_name    VARCHAR(100),
    consignee_address VARCHAR(255),
    cargo_desc        TEXT,
    cargo_type        VARCHAR(50),
    weight_kg         DECIMAL(10,2),
    container_type    VARCHAR(20),
    container_qty     INT DEFAULT 1,
    origin_port       VARCHAR(10),
    etd               DATE,
    eta               DATE NULL,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (shipment_id),
    CONSTRAINT fk_shipment_details_shipment FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO shipment_details (shipment_id, shipper_name, shipper_address, consignee_name, consignee_address, cargo_desc, cargo_type, weight_kg, container_type, container_qty, origin_port, etd, eta) VALUES
(1, 'John Smith', '123 Ocean Ave, Los Angeles, USA', 'Shanghai Retail Group', 'No.88 Nanjing Rd, Shanghai, China', 'Linh kiện điện tử cao cấp', 'Thường', 12500.00, '40GP', 2, 'US LAX', '2024-05-10', '2024-05-28'),
(2, 'John Smith', '123 Ocean Ave, Los Angeles, USA', 'Singa Fresh Market', '10 Marina Blvd, Singapore', 'Nông sản đông lạnh', 'Lạnh', 8400.00, '20GP', 1, 'US LAX', '2024-05-15', '2024-06-02'),
(3, 'Alice Wong', '88 Nathan Rd, Kowloon, Hong Kong', 'Dubai Petrochemicals', 'Jebel Ali Free Zone, Dubai, UAE', 'Hóa chất công nghiệp nhẹ', 'Nguy hiểm', 15200.00, '40HC', 3, 'CN SHA', '2024-05-12', '2024-05-30'),
(4, 'Alice Wong', '88 Nathan Rd, Kowloon, Hong Kong', 'EuroPort Distribution BV', 'Maasvlakte 2, Rotterdam, Netherlands', 'Hàng may mặc gia dụng', 'Thường', 9800.00, '40GP', 1, 'CN NGB', '2024-04-20', '2024-05-18'),
(5, 'Maria Garcia', 'Av. Diagonal 450, Barcelona, Spain', 'Pacific Auto Parts LA', '200 Harbor Blvd, Los Angeles, USA', 'Phụ tùng ô tô và cơ khí', 'Thường', 14000.00, '40GP', 2, 'NL RTM', '2024-05-01', '2024-05-22');

-- ---- shipment_events -------------------------------------------------------
CREATE TABLE IF NOT EXISTS shipment_events (
    id          INT NOT NULL AUTO_INCREMENT,
    shipment_id INT NOT NULL,
    status      VARCHAR(40) NOT NULL,
    location    VARCHAR(100),
    note        TEXT,
    created_by  INT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_shipment_events_shipment FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE,
    CONSTRAINT fk_shipment_events_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO shipment_events (id, shipment_id, status, location, note, created_by, created_at) VALUES
(1, 1, 'Booked', 'US LAX', 'Đơn hàng đã được đặt và tiếp nhận', 1, '2024-05-08 09:00:00'),
(2, 1, 'In Transit', 'Pacific Ocean', 'Tàu vận tải đã rời cảng Los Angeles', 4, '2024-05-10 14:30:00'),
(3, 2, 'Booked', 'US LAX', 'Đơn hàng đã được tạo thành công', 1, '2024-05-13 10:00:00'),
(4, 2, 'At Port', 'SG SIN', 'Hàng đã cập cảng Singapore, đang chờ bốc dỡ', 4, '2024-05-20 16:15:00'),
(5, 3, 'Booked', 'CN SHA', 'Đơn hàng tiếp nhận tại Thượng Hải', 1, '2024-05-11 08:30:00'),
(6, 3, 'In Transit', 'Indian Ocean', 'Đang vận chuyển qua vùng biển Ấn Độ Dương', 4, '2024-05-14 11:00:00'),
(7, 3, 'Customs Hold', 'AE DXB', 'Hàng hoá đang được hải quan kiểm hoá giấy tờ chứng nhận', 4, '2024-05-19 15:45:00'),
(8, 4, 'Booked', 'CN NGB', 'Đơn hàng tiếp nhận tại Ninh Ba', 1, '2024-04-18 10:00:00'),
(9, 4, 'In Transit', 'Red Sea', 'Đang hải trình đến châu Âu', 4, '2024-04-22 13:00:00'),
(10, 4, 'Delivered', 'NL RTM', 'Đã giao hàng thành công tới kho người nhận', 4, '2024-05-18 17:00:00'),
(11, 5, 'Booked', 'NL RTM', 'Đơn hàng khởi tạo tại Rotterdam', 1, '2024-04-29 09:30:00'),
(12, 5, 'In Transit', 'Atlantic Ocean', 'Đang vận chuyển xuyên Đại Tây Dương', 4, '2024-05-02 12:00:00'),
(13, 5, 'Out for Delivery', 'US LAX', 'Hàng đang trên đường vận chuyển tới kho giao cuối', 4, '2024-05-22 08:00:00');

-- ---- notifications ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    id          INT NOT NULL AUTO_INCREMENT,
    user_id     INT NOT NULL,
    shipment_id INT NULL,
    message     TEXT NOT NULL,
    is_read     TINYINT DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_notifications_shipment FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---- mail_outbox -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS mail_outbox (
    id         INT NOT NULL AUTO_INCREMENT,
    to_email   VARCHAR(150) NOT NULL,
    subject    VARCHAR(200) NOT NULL,
    body       TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---- contact_messages ------------------------------------------------------
CREATE TABLE IF NOT EXISTS contact_messages (
    id         INT NOT NULL AUTO_INCREMENT,
    full_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL,
    phone      VARCHAR(20),
    message    TEXT NOT NULL,
    is_handled TINYINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---- freight_rates ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS freight_rates (
    id              INT NOT NULL AUTO_INCREMENT,
    origin_port     VARCHAR(10) NOT NULL,
    dest_port       VARCHAR(10) NOT NULL,
    container_type  VARCHAR(20) NOT NULL,
    base_price_usd  DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO freight_rates (id, origin_port, dest_port, container_type, base_price_usd) VALUES
(1, 'CN SHA', 'NL RTM', '20GP', 1850.00),
(2, 'CN SHA', 'NL RTM', '40GP', 3100.00),
(3, 'CN SHA', 'NL RTM', '40HC', 3400.00),
(4, 'CN SHA', 'US LAX', '20GP', 2100.00),
(5, 'CN SHA', 'US LAX', '40GP', 3500.00),
(6, 'SG SIN', 'NL RTM', '20GP', 1600.00),
(7, 'SG SIN', 'NL RTM', '40GP', 2800.00),
(8, 'CN NGB', 'AE DXB', '20GP', 1400.00),
(9, 'CN NGB', 'AE DXB', '40GP', 2400.00),
(10, 'US LAX', 'CN SHA', '20GP', 1200.00),
(11, 'US LAX', 'CN SHA', '40GP', 2000.00),
(12, 'NL RTM', 'US LAX', '20GP', 1900.00),
(13, 'NL RTM', 'US LAX', '40GP', 3200.00);

-- ============================================================================
--  DATABASE: dev  (muc tieu enumeration lien-DB)
-- ============================================================================
CREATE DATABASE IF NOT EXISTS dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dev;

-- ---- credentials (muc tieu dump) ------------------------------------------
CREATE TABLE IF NOT EXISTS credentials (
    id            INT NOT NULL AUTO_INCREMENT,
    username      VARCHAR(100),
    password_hash VARCHAR(64),
    api_key       VARCHAR(64),
    PRIMARY KEY (id)
);

-- password_hash = md5() cua mat khau that (de hoc vien crack neu muon)
INSERT INTO credentials (username, password_hash, api_key) VALUES
('dev_admin', '392037dbba51f692776d6cefb6dd546d', 'DEV-KEY-super-secret-0xC0FFEE'),
('backup_svc','9da2c9bcdf39d8610954e0e11ea8f45f', 'DEV-KEY-backup-4b1dp0nd');

-- ---- flags (co theo tung ky thuat — chung minh khai thac thanh cong) -------
CREATE TABLE IF NOT EXISTS flags (
    id        INT NOT NULL AUTO_INCREMENT,
    technique VARCHAR(60),
    flag      VARCHAR(120),
    PRIMARY KEY (id)
);

INSERT INTO flags (technique, flag) VALUES
('inband-union',   'ILF{un10n_b4s3d_dump_c0mpl3t3}'),
('inband-error',   'ILF{3rr0r_b4s3d_3xtr4ctv4lu3}'),
('blind-boolean',  'ILF{bl1nd_b00l34n_ch4r_by_ch4r}'),
('blind-time',     'ILF{t1m3_b4s3d_sl33p_5s}'),
('out-of-band',    'ILF{00b_3xf1l_v14_dns_ch4nn3l}'),
('stacked-query',  'ILF{st4ck3d_mult1_qu3ry_pwn3d}'),
('file-read',      'ILF{l04d_f1l3_r34d_3tc_p4sswd}'),
('file-write',     'ILF{1nt0_0utf1l3_w3bsh3ll_rc3}');

-- ============================================================================
--  Quay lai DB ung dung mac dinh
-- ============================================================================
USE ilfreight;
