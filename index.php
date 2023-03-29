<?php
require_once "includes/config.php";
require_once "includes/Twitter/autoload.php";
use Abraham\TwitterOAuth\TwitterOAuth;
session_start();
$button = "";
$logged = false;
if(isset($_GET['oauth_verifier']) && isset($_GET['oauth_token']) && isset($_SESSION['oauth_token']) && $_GET['oauth_token'] == $_SESSION['oauth_token']){
    $connectTwitter3 = new TwitterOAuth(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, $_SESSION['oauth_token'], $_SESSION['oauth_token_secret'] );
    $access_token = $connectTwitter3->oauth('oauth/access_token', array('oauth_verifier' => $_GET['oauth_verifier']));
    $_SESSION['access_twitter'] = $access_token;
    if(isset($_SESSION['access_twitter']) && $_SESSION['access_twitter']){
        $oauthenticate = $_SESSION['access_twitter']['oauth_token'];
        $oauthenticate_secret = $_SESSION['access_twitter']['oauth_token_secret'];
        $verifier = new TwitterOAuth(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, $oauthenticate, $oauthenticate_secret);
        $getUser = $verifier->get('account/verify_credentials');
        if(!property_exists($getUser, 'error')){
            $id = $getUser->id;
            $username = $getUser->screen_name;
            $fullname = $getUser->name;
            if(isset($id) && !empty($id)){
                $statement = $pdo->prepare("SELECT * FROM users WHERE userid=?");
            	$statement->execute(array($id));
            	$total = $statement->rowCount();
            	if($total>0){
            	    $statement = $pdo->prepare("UPDATE users SET fullname=?, username=?, modified=? WHERE userid=?");
                	$statement->execute(array($fullname,$username,time(),$id));
            	}else{
                    $statement = $pdo->prepare("INSERT IGNORE INTO users (fullname,userid,phone,username,created,modified) VALUES (?,?,?,?,?,?)");
                	$statement->execute(array($fullname,$id,"",$username,time(),time()));
            	}
                $logged = true;
            }
        }
    }
}else{
    $connectTwitter1 = new TwitterOAuth(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET);
    $request_token = $connectTwitter1->oauth('oauth/request_token', array('oauth_callback' => TWITTER_REDIRECT_URL));
    $_SESSION['oauth_token'] = $request_token['oauth_token'];
    $_SESSION['oauth_token_secret'] = $request_token['oauth_token_secret'];
    $connectTwitter2 = new TwitterOAuth(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, $_SESSION['oauth_token'], $_SESSION['oauth_token_secret']);
    $verify_authentication = $connectTwitter2->url('oauth/authenticate', array('oauth_token' => $request_token['oauth_token']));
    $button = htmlspecialchars($verify_authentication);
}
?>
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1 maximum-scale=1">
        <meta name="description" content="Twitter Videos to WhatsApp">
        <meta name="author" content="NodeTent">
        <title>t2w.app - Send Twitter Videos to WhatsApp</title>
        <link rel="shortcut icon" href="assets/images/favicon.png" type="image/x-icon">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">
        <link href="assets/css/bootstrap.min.css" rel="stylesheet">
        <link href="assets/css/intlTelInput.css?k=k" rel="stylesheet">
        <link href="assets/css/style.css" rel="stylesheet">
    </head>
    <body>
    	<div id="preloader">
    		<div data-loader="circle-side"></div>
    	</div>
    	<div class="container-fluid">
    	    <div class="row row-height">
    	        <div class="col-lg-6 background-image p-0" data-background="linear-gradient(to bottom right, #1DA1F2, #25D366)">
    	            <div class="content-left-wrapper">
    	                <a href="/" id="logo"><img src="assets/images/logo.svg" alt="t2w.app" height="100%"></a>
    	                <div>
    	                    <h1>t2w.app -beta</h1><br>
    	                    <p>Connect your Twitter account.</p>
    	                    <p>Link your WhatsApp number.</p>
    	                    <p>Call @Send2WhatsApp on any Twitter video and get it delivered to your WhatsApp in seconds.</p>
    	                    <a href="javascript:void(0);" data-bs-toggle="modal" data-bs-target="#faq" class="btn_1 black rounded pulse_bt">F.A.Q</a>
    	               </div>
    	            </div>
    	        </div>
    	        <div class="col-lg-6 d-flex flex-column content-right">
    	            <div class="container my-auto py-5">
    	                <div class="row">
    	                    <div class="col-lg-9 col-xl-7 mx-auto">
    	                        <?php if($logged){?>
    	                        <form id="link">
    								<div class="divider"><span>Link @<?=$username?> with your WhatsApp</span></div>
    								<div class="form-group">
    	                                <label for="phone">WhatsApp Phone Number</label>
    	                                <span id="valid-msg" class="hide">✓ Valid</span><span id="error-msg" class="hide"></span>
    	                                <input type="tel" id="phone" name="phone" class="form-control" required>
    	                                <input type="hidden" id="realphone" name="realphone" value="">
    	                                <input type="hidden" id="id" name="id" value="<?=$id?>">
    	                            </div>
    	                            <div id="pass-info" class="clearfix"></div>
    	                                <div class="mb-4">
    	                                    <label class="container_check">I agree to the <a href="javascript:void(0);" data-bs-toggle="modal" data-bs-target="#terms-txt">Terms and Privacy Policy</a>.
    	                                        <input type="checkbox" required><span class="checkmark"></span>
    	                                    </label>
    	                                </div>
    	                            <button type="submit" class="btn_1 full-width" id="submit">Connect</button>
    	                        </form>
    	                        <p class="hide text-center mt-3 mb-0" id="tip" style="color:darkgreen;">Tip: Videos will be sent to you from <b>+2348089047173</b> have it saved on your contact list for convinience.</p>
    	                        <?php }else{?>
    	                        <a href="<?=$button?>" class="social_bt"><i class="fa fa-twitter"></i>&nbsp;Connect your Twitter</a>
    	                        <?php }?>
    	                    </div>
    	                </div>
    	            </div>
    	            <div class="container pb-3 copy">© t2w.app <?=date("Y")?> - All Rights Reserved.</div>
    	        </div>
    	    </div>
    	</div>
    	<div class="modal fade" id="terms-txt" tabindex="-1" role="dialog" aria-labelledby="termsLabel" aria-hidden="true">
    		<div class="modal-dialog modal-dialog-centered">
    			<div class="modal-content">
    				<div class="modal-header">
    					<h4 class="modal-title" id="termsLabel">Terms and Conditions</h4>
    					<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
    				</div>
    				<div class="modal-body">
    				    <ol>
    					    <li>The providers ("we", "us", "our") of this web site and all its provider/owner-operated subdomains ("Service") are not responsible for any user-generated content ("Content") and accounts.</li>
    					    <li>Content submitted express the views of their author only.</li>
    					    <li>This Service is only available to users who are at least 18 years old. If you are younger than this, please do not use this Service.</li>
    					    <li>All Content you submit, upload, or otherwise make available to the Service may be reviewed by us.</li>
    					    <li>You agree to not use the Service to submit or link to any Content which is illegal by US law or malicious (as in: malware, spam, phishing, etc.).</li>
    					    <li>You are entirely responsible for the content of, and any harm resulting from, that Content or your conduct.</li>
    					    <li>We may remove or modify any Content submitted at any time, with or without cause, with or without notice.</li>
    					    <li>You may not use the service as a component in another, third party commercial service without prior approval.</li>
    					    <li>Requests for Content to be removed or modified will be undertaken only at our discretion.</li>
    					    <li>We may terminate your access to all or any part of the Service at any time, with or without cause, with or without notice.</li>
    					    <li>These terms may be changed at any time, but notice will be appropriately posted by us on each service where the change applies.</li>
    					    <li>If you do not agree with these terms, please do not use the Service. Use of the Service constitutes acceptance of these terms.</li>
    					    <li>Please note that some portions of the Service are not under our sole control, and are instead provided to members for no charge as a courtesy. These services are still bound by the terms and conditions.</li>
    					</ol>
    				</div>
    				<div class="modal-footer">
    					<button type="button" class="btn_1" data-bs-dismiss="modal">Close</button>
    				</div>
    			</div>
    		</div>
    	</div>
    	<div class="modal fade" id="faq" tabindex="-1" role="dialog" aria-labelledby="faqLabel" aria-hidden="true">
    		<div class="modal-dialog modal-dialog-centered">
    			<div class="modal-content">
    				<div class="modal-header">
    					<h4 class="modal-title" id="faqLabel">FAQ</h4>
    					<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
    				</div>
    				<div class="modal-body">
    				    <h6>WTF is this?</h6>
    					<p>t2w.app is a simple to use free video downloading service where you can send twitter video clips easily to your whatsapp for local usage.</p>
    					<h6>How exactly does this work?</h6>
    					<p>You come to this page which you already are, then connect your Twitter account by clicking on that button (don't worry, nothing shady, we just need your twitter username to authenticate you). Then you link your WhatsApp number. Then you leave this page and forget you ever visited here.</p>
    					<p>Get back to Twitter, see a video you like to save? mention @Send2WhatsApp under the tweet, our server will quickly run the errand to process the video and try to deliver it to the WhatsApp number you registered earlier on.</p>
    					<p>Rinse and repeat.</p>
                        <h6>Why should I use this?</h6>
                        <p>Fuck do I know, you tell me.</p>
                        <h6>Having trouble linking my Twitter account</h6>
                        <p>If you're having this issue, you're most likely on mobile and specifically iOS, the issue is from Twitter API, you can workaround this on a PC if you have one, if not mail me to link your account manually.</p>
                        <h6>Is my number safe with you?</h6>
                        <p>Sure, I will make sure never to let your number public as I regard it as private data. If I ever default, contact the authorities and have them serve me with a court order, warrant, etc. But I'd prefer not to wake up at 3am with a shotgun in my face, I rather keep it safe.</p>
                        <h6>I didnt get any videos on my whatsapp after setup?</h6>
                        <p>Make sure the whatsapp number you provided is correct, you can relink your account with the usual setup process to reenter the number, if the problem persist, shoot a mail with your Twitter username to help@t2w.app</p>
                        <h6>Can I unlink my account?</h6>
                        <p>Send a strongly worded email to help@t2w.app with proof of account and I will try to get back to you within 24 hours.</p>
                        <h6>I have a question...</h6>
                        <p>Send a mail to help@t2w.app let's talk!</p>
    				</div>
    				<div class="modal-footer">
    					<button type="button" class="btn_1" data-bs-dismiss="modal">Close</button>
    				</div>
    			</div>
    		</div>
    	</div>
    	<script src="assets/js/vendor.js"></script>
    	<script src="https://cdn.jsdelivr.net/npm/intl-tel-input@17.0.3/build/js/intlTelInput.js" charset="utf-8"></script>
    	<script src="assets/js/main.js?t=<?=time()?>"></script>
    </body>
</html>