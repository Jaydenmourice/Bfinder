<?php
// User management endpoint

// Hardcoded credentials (triggers: Hardcoded credential)
$db_password = "SuperSecret123";
$api_key     = "live_key_abc987xyz";

// Unvalidated superglobal (triggers: Unvalidated user input from superglobal)
$username = $_GET['username'];
$userId   = $_POST['id'];
$filter   = $_REQUEST['filter'];

// Direct echo of user input — XSS (triggers: Potential XSS direct echo)
echo $_GET['username'];
print "Welcome " . $_POST['name'];
printf("Hello %s, your ID is %d", $_GET['user'], $_POST['id']);

// eval (triggers: Use of eval() in PHP)
$code = $_POST['snippet'];
eval($code);

// Command injection (triggers: Potential command injection)
$file   = $_GET['filename'];
$result = shell_exec("cat " . $file);
$ping   = exec("ping -c 1 " . $_GET['host']);
system("convert " . $_POST['image'] . " output.png");

// SQL injection — old mysql_query (triggers: Potential SQL injection)
$name  = $_GET['name'];
$query = mysql_query("SELECT * FROM users WHERE name = '" . $name . "'");

// SQL injection — PDO (triggers: Potential SQL injection)
$id  = $_POST['id'];
$pdo->query("SELECT * FROM orders WHERE id = " . $id);

// SQL injection — string concat pattern
$search = $_GET['q'];
$sql    = "SELECT * FROM products WHERE name LIKE '%" . $search . "%'";

// File inclusion with variable (triggers: Potential file inclusion LFI/RFI)
$page   = $_GET['page'];
include($page);
require_once($page . ".php");

// Open redirect (triggers: Open redirect in PHP header)
$next = $_GET['next'];
header('Location: ' . $next);
exit;
?>
