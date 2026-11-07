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

INSERT INTO news (title, body) VALUES
('Mo rong tuyen Shanghai - Rotterdam', 'IlFreight cong bo tuyen van tai moi...'),
('Nang cap he thong tra cuu van don',  'Cong cu tra cuu tracking duoc cai tien...');

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
