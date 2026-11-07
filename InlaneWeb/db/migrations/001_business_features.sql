-- ============================================================================
-- Migration: 001_business_features.sql
-- Bo sung cac bang nghiep vu va seed du lieu cho InlaneWeb.
-- Co the chay lai nhieu lan ma khong loi (idempotent).
-- ============================================================================
USE ilfreight;

-- 1. user_profiles
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

-- 2. password_resets
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

-- 3. shipment_details
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

-- 4. shipment_events
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

-- 5. notifications
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

-- 6. mail_outbox
CREATE TABLE IF NOT EXISTS mail_outbox (
    id         INT NOT NULL AUTO_INCREMENT,
    to_email   VARCHAR(150) NOT NULL,
    subject    VARCHAR(200) NOT NULL,
    body       TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. contact_messages
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

-- 8. freight_rates
CREATE TABLE IF NOT EXISTS freight_rates (
    id              INT NOT NULL AUTO_INCREMENT,
    origin_port     VARCHAR(10) NOT NULL,
    dest_port       VARCHAR(10) NOT NULL,
    container_type  VARCHAR(20) NOT NULL,
    base_price_usd  DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- SEED DATA (dung INSERT IGNORE de dam bao chay lai nhieu lan an toan)
-- ----------------------------------------------------------------------------

-- Seed user_profiles cho 4 users mac dinh
INSERT IGNORE INTO user_profiles (user_id, full_name, phone, company, address, is_locked, accepted_terms_at) VALUES
(1, 'Admin IlFreight', '0901234567', 'IlFreight HQ', 'Hai Phong, Vietnam', 0, NOW()),
(2, 'John Smith', '+1-555-0199', 'Smith Trading Co.', 'Los Angeles, USA', 0, NOW()),
(3, 'Alice Wong', '+852-9123-4567', 'Wong Import Export Ltd.', 'Hong Kong', 0, NOW()),
(4, 'Maria Garcia', '+34-600-112233', 'Garcia Logistics S.L.', 'Barcelona, Spain', 0, NOW());

-- Seed shipment_details cho 5 van don hien co
INSERT IGNORE INTO shipment_details (shipment_id, shipper_name, shipper_address, consignee_name, consignee_address, cargo_desc, cargo_type, weight_kg, container_type, container_qty, origin_port, etd, eta) VALUES
(1, 'John Smith', '123 Ocean Ave, Los Angeles, USA', 'Shanghai Retail Group', 'No.88 Nanjing Rd, Shanghai, China', 'Linh kiện điện tử cao cấp', 'Thường', 12500.00, '40GP', 2, 'US LAX', '2024-05-10', '2024-05-28'),
(2, 'John Smith', '123 Ocean Ave, Los Angeles, USA', 'Singa Fresh Market', '10 Marina Blvd, Singapore', 'Nông sản đông lạnh', 'Lạnh', 8400.00, '20GP', 1, 'US LAX', '2024-05-15', '2024-06-02'),
(3, 'Alice Wong', '88 Nathan Rd, Kowloon, Hong Kong', 'Dubai Petrochemicals', 'Jebel Ali Free Zone, Dubai, UAE', 'Hóa chất công nghiệp nhẹ', 'Nguy hiểm', 15200.00, '40HC', 3, 'CN SHA', '2024-05-12', '2024-05-30'),
(4, 'Alice Wong', '88 Nathan Rd, Kowloon, Hong Kong', 'EuroPort Distribution BV', 'Maasvlakte 2, Rotterdam, Netherlands', 'Hàng may mặc gia dụng', 'Thường', 9800.00, '40GP', 1, 'CN NGB', '2024-04-20', '2024-05-18'),
(5, 'Maria Garcia', 'Av. Diagonal 450, Barcelona, Spain', 'Pacific Auto Parts LA', '200 Harbor Blvd, Los Angeles, USA', 'Phụ tùng ô tô và cơ khí', 'Thường', 14000.00, '40GP', 2, 'NL RTM', '2024-05-01', '2024-05-22');

-- Seed shipment_events cho 5 van don hien co
INSERT IGNORE INTO shipment_events (id, shipment_id, status, location, note, created_by, created_at) VALUES
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

-- Seed freight_rates giua cac cang co san
INSERT IGNORE INTO freight_rates (id, origin_port, dest_port, container_type, base_price_usd) VALUES
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
