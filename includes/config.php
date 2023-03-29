<?php
date_default_timezone_set("Africa/Lagos");
$dbhost = "";
$dbname = "";
$dbuser = "";
$dbpass = "";
try {
	$pdo = new PDO("mysql:host={$dbhost};dbname={$dbname}", $dbuser, $dbpass);
	$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
}catch(PDOException $exception){
	echo "Connection Error: ".$exception->getMessage();
}
define("TWITTER_CONSUMER_KEY", "");
define("TWITTER_CONSUMER_SECRET", "");
define("TWITTER_REDIRECT_URL", "");
?>