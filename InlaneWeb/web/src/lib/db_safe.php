<?php
/**
 * db_safe.php — Safe Database Query Wrappers using Prepared Statements.
 * Chuyen dung cho code moi de ngan ngua tuyet doi SQL Injection.
 */

require_once __DIR__ . '/db.php';
require_once __DIR__ . '/schema.php';

/**
 * db_prepare_and_execute() — Helper chung de chuan bi, bind tham so va thuc thi statement.
 * Tu dong khoi tao cac bang mo rong neu DB chua chay init.sql ban moi (errno 1146).
 */
function db_prepare_and_execute(\mysqli $conn, string $sql, string $types = '', array $params = []): \mysqli_stmt
{
    db_ensure_schema($conn);

    $stmt = mysqli_prepare($conn, $sql);
    if (!$stmt && mysqli_errno($conn) === 1146) {
        db_ensure_schema($conn, true);
        $stmt = mysqli_prepare($conn, $sql);
    }

    if (!$stmt) {
        $err = mysqli_error($conn);
        InlaneLogger::logSqlError($sql, $err, mysqli_errno($conn));
        throw new \RuntimeException('DB Prepare Error: ' . $err);
    }

    if ($types !== '' && !empty($params)) {
        mysqli_stmt_bind_param($stmt, $types, ...$params);
    }

    if (!mysqli_stmt_execute($stmt)) {
        $err = mysqli_stmt_error($stmt);
        InlaneLogger::logSqlError($sql, $err, mysqli_stmt_errno($stmt));
        mysqli_stmt_close($stmt);
        throw new \RuntimeException('DB Execute Error: ' . $err);
    }

    return $stmt;
}

/**
 * db_select() — Thuc thi SELECT voi prepared statement va tra ve mang associative rows.
 */
function db_select(string $sql, string $types = '', array $params = []): array
{
    $conn = db();
    $stmt = db_prepare_and_execute($conn, $sql, $types, $params);

    $result = mysqli_stmt_get_result($stmt);
    $rows = [];
    if ($result) {
        while ($row = mysqli_fetch_assoc($result)) {
            $rows[] = $row;
        }
        mysqli_free_result($result);
    }
    mysqli_stmt_close($stmt);
    return $rows;
}

/**
 * db_select_one() — Thuc thi SELECT va tra ve 1 row duy nhat hoac null.
 */
function db_select_one(string $sql, string $types = '', array $params = []): ?array
{
    $rows = db_select($sql, $types, $params);
    return !empty($rows) ? $rows[0] : null;
}

/**
 * db_execute() — Thuc thi INSERT / UPDATE / DELETE va tra ve so dong bi anh huong (affected_rows).
 */
function db_execute(string $sql, string $types = '', array $params = []): int
{
    $conn = db();
    $stmt = db_prepare_and_execute($conn, $sql, $types, $params);
    $affected = mysqli_stmt_affected_rows($stmt);
    mysqli_stmt_close($stmt);
    return $affected;
}

/**
 * db_insert() — Thuc thi INSERT va tra ve insert_id (ID vua duoc tao).
 */
function db_insert(string $sql, string $types = '', array $params = []): int
{
    $conn = db();
    $stmt = db_prepare_and_execute($conn, $sql, $types, $params);
    $insertId = (int)mysqli_stmt_insert_id($stmt);
    mysqli_stmt_close($stmt);
    return $insertId;
}
