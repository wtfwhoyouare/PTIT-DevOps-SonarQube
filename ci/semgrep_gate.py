"""Chốt chặn An ninh Semgrep (Semgrep Security Gate Enforcement).

Hiện thực hóa nguyên lý Shift-Left Security & Break-the-Build trong DevSecOps:
- Tự động phân tích tệp kết quả quét an ninh SAST: reports/semgrep/semgrep.json.
- Kiểm tra các lỗ hổng an ninh có độ nghiêm trọng mức ERROR / High.
- Xuất GitHub Actions Workflow Annotations (::error) ghim trực tiếp lên Pull Request.
- Khi biến môi trường ENFORCE_SECURITY_GATE=true (mặc định):
  + Nếu phát hiện lỗ hổng mức ERROR -> In cảnh báo và thoát với Exit Code 1 (CHẶN ĐỨNG PIPELINE).
  + Nếu không có lỗi ERROR -> In xác nhận an toàn và thoát với Exit Code 0 (CHO PHÉP MERGE).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

# Đảm bảo mã hóa UTF-8 trên mọi hệ điều hành (Windows / Linux runner)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SEMGREP_JSON = ROOT / "reports/semgrep/semgrep.json"


def log_github_error(title: str, message: str, file_path: str = "", line: int = 0) -> None:
    """In thông báo lỗi ra stderr theo cú pháp Annotation chuẩn của GitHub Actions.

    Cú pháp này giúp hiển thị cảnh báo đỏ trực tiếp tại dòng code vi phạm trên giao diện GitHub PR.
    """
    escaped_msg = message.replace("\n", "%0A")
    loc_str = ""
    if file_path:
        loc_str = f" file={file_path}"
        if line > 0:
            loc_str += f",line={line}"
    print(f"::error{loc_str} title={title}::{escaped_msg}", file=sys.stderr)


def evaluate_gate(json_path: Path | None = None) -> int:
    """Đánh giá kết quả quét của Semgrep đối chiếu với tiêu chuẩn Security Gate.

    Args:
        json_path: Đường dẫn tệp kết quả Semgrep JSON (mặc định reports/semgrep/semgrep.json).

    Returns:
        0 nếu đạt chuẩn (hoặc chế độ chỉ báo cáo report-only).
        1 nếu phát hiện vi phạm và chế độ chốt chặn đang được kích hoạt.
    """
    target_file = json_path or SEMGREP_JSON
    if not target_file.exists():
        print(f"⚠️ [Security Gate] Không tìm thấy tệp kết quả: {target_file}", file=sys.stderr)
        log_github_error("Missing Scan Results", f"Không tìm thấy tệp kết quả {target_file}")
        return 1

    try:
        data = json.loads(target_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ [Security Gate] Lỗi đọc dữ liệu Semgrep JSON: {e}", file=sys.stderr)
        return 1

    # Phân loại các phát hiện an ninh theo mức độ nghiêm trọng
    results = data.get("results", [])
    errors = [r for r in results if r.get("extra", {}).get("severity") == "ERROR"]
    warnings = [r for r in results if r.get("extra", {}).get("severity") == "WARNING"]
    infos = [r for r in results if r.get("extra", {}).get("severity") == "INFO"]

    total = len(results)
    # Kiểm tra biến môi trường kích hoạt chốt chặn (mặc định là true)
    enforce = os.environ.get("ENFORCE_SECURITY_GATE", "true").lower() == "true"

    print("\n" + "=" * 78)
    print("🛡️  ĐÁNH GIÁ CHỐT CHẶN AN NINH MÃ NGUỒN: SEMGREP SECURITY GATE (STAGE 2)")
    print("=" * 78)
    print(f"📊 Tổng số phát hiện SAST: {total}")
    print(f"   🔴 Mức độ nghiêm trọng (ERROR / HIGH):   {len(errors)}")
    print(f"   🟡 Mức độ cảnh báo    (WARNING / MED):   {len(warnings)}")
    print(f"   🔵 Mức độ thông tin   (INFO / LOW):      {len(infos)}")
    print(f"⚙️  Chế độ kiểm soát: {'BẮT BUỘC CHẶN (STRICT ENFORCEMENT)' if enforce else 'CHỈ BÁO CÁO (REPORT-ONLY)'}")
    print("-" * 78)

    # Nếu phát hiện lỗ hổng mức ERROR
    if errors:
        print(f"\n❌ PHÁT HIỆN {len(errors)} LỖ HỔNG BẢO MẬT MỨC ĐỘ CAO (ERROR):", file=sys.stderr)
        for idx, err in enumerate(errors, 1):
            check_id = err.get("check_id", "unknown")
            path = err.get("path", "")
            start_line = err.get("start", {}).get("line", 0)
            msg = err.get("extra", {}).get("message", "").strip().splitlines()[0]
            cwe = err.get("extra", {}).get("metadata", {}).get("cwe", "")
            if isinstance(cwe, list):
                cwe = ", ".join(cwe)

            # In chi tiết lỗi ra console
            print(f"  [{idx:02d}] 🛑 {path}:{start_line} | {cwe}", file=sys.stderr)
            print(f"       Quy tắc: {check_id}", file=sys.stderr)
            print(f"       Chi tiết: {msg}\n", file=sys.stderr)

            # Đẩy chú thích lỗi lên giao diện GitHub Actions PR
            log_github_error(
                f"Security Gate Blocker ({cwe or check_id})",
                f"[{check_id}] tại {path}:{start_line} - {msg}",
                file_path=path,
                line=start_line,
            )

        print("=" * 78, file=sys.stderr)
        if enforce:
            # Chặn đứng pipeline (Break-the-Build)
            print("🛑 [CHẶN ĐỨNG PIPELINE - BREAK-THE-BUILD]", file=sys.stderr)
            print("Chính sách Security-as-Code (SaC) quy định KHÔNG ĐƯỢC PHÉP tồn tại lỗ hổng", file=sys.stderr)
            print("mức độ ERROR / HIGH trước khi hợp nhất vào nhánh 'dev' hoặc 'main'.", file=sys.stderr)
            print("Pull Request này đã bị CHẶN ĐỨNG tự động để bảo vệ môi trường vận hành.", file=sys.stderr)
            print("=" * 78 + "\n", file=sys.stderr)
            return 1
        else:
            print("⚠️ CẢNH BÁO: Phát hiện vi phạm an ninh nhưng chế độ kiểm soát đang là REPORT-ONLY.", file=sys.stderr)
            print("Pipeline tiếp tục thực thi nhưng các lỗ hổng cần được ghi nhận và khắc phục.", file=sys.stderr)
            print("=" * 78 + "\n", file=sys.stderr)
            return 0

    # Nếu không có lỗ hổng mức ERROR
    print("✅ XÁC THỰC THÀNH CÔNG: Không phát hiện lỗ hổng bảo mật nghiêm trọng!")
    print("Mã nguồn đáp ứng toàn bộ tiêu chuẩn Shift-Left Security Gate.")
    print("=" * 78 + "\n")
    return 0


def main() -> None:
    """Điểm nhập cảnh chính khi chạy script độc lập."""
    sys.exit(evaluate_gate())


if __name__ == "__main__":
    main()
