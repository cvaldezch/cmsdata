$(document).ready(function() {
	$(".btn-materials").on("click", materialsBalanace);
	$(".btn-inventory").on("click", allmaterials);
});
// functions
var materialsBalanace = function (event) {
	event.preventDefault();
	$().toastmessage("showToast",{
		text: 'Wanth generate balance material?.',
		type: 'confirm',
		sticky: true,
		buttons: [{value:'Yes'}, {value:'No'}],
		success: function (result) {
			if (result == "Yes") {
				var $code = $("input[name=code]");
				if ($code.val() != '') {
					var data = new Object();
					data['code'] = $code.val();
					data['type'] = "one";
					data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
					$.post('', data, function(response) {
						console.log(response);
						if (response.status) {
							$().toastmessage("showNoticeToast","Transaction Success sfgf.");
						}else{
							$().toastmessage("showWarningToast","Transaction not found!");
						};
					});
				}else{
					$().toastmessage("showWarningToast","Not found code, enter code");
					$code.focus();
				};
			};
		}
	});
	
}
var allmaterials = function (event) {
	event.preventDefault();
	$().toastmessage("showToast", {
		text: 'Wanth register all materials, note this is process may take minutes?. Please wait.',
		type: 'confirm',
		sticky: true,
		buttons: [{value:'Yes'}, {value:'No'}],
		success: function (result) {
			if (result == 'Yes') {
				$(".modal").modal("show");
				var data = new Object();
				data['type'] = "all";
				data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
				$.post('', data, function(response) {
					//console.log(response);
					$(".modal").modal("hide");
					if (response.status) {
						var msg = response.msg.split("|");
						$().toastmessage("showNoticeToast", "Success Transaction<br /> Total Success: "+msg[0]+" <br /> Total Fail: "+msg[1]);
					}else{
						$().toastmessage("showWarningToast","Transaction not found!");
					};
				});
			};
		}
	});
}