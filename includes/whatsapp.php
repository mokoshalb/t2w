<?php
include "config.php";
if(isset($_POST['realphone']) && isset($_POST['id'])) {
	$phone = $_POST['realphone'];
	if($phone == "+2348011223344"){ //replace with your number to avoid self sending error
	    http_response_code(403);
	    exit;
	}
	$id = $_POST['id'];
	$valid = 1; //do extensive number verification later
    if($valid == 1) {
		$statement = $pdo->prepare("UPDATE users SET phone=? WHERE userid=?");
        $statement->execute(array($phone,$id));
    }
}else{
    http_response_code(403);
    exit;
}
?>