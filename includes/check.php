<?php
include "config.php";
if(isset($_REQUEST['id'])){
	$id = $_REQUEST['id'];
    $statement = $pdo->prepare("SELECT * FROM users WHERE userid=?");
	$statement->execute(array($id));
	$total = $statement->rowCount();
	if($total>0){
	    $details = $statement->fetch();
        echo $details["phone"];
	}else{
        echo "NULL";
	}
}else{
    echo "NULL";
}
?>