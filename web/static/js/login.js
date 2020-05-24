function login(){
	console.log('LOG USER');
	var username = $('#username').val();
	var password= $ ('#password').val();
	console.log("DATA>", username, password);
	var credentials = {
		'username': username, 
		'password': password
	};
	$.post({
		url: '/authenticate', 
		type: 'post',
		dataType: 'json',
		contentType: 'application/json',
		success: function (data){
			console.log('Authenticated!');
			alert('Autenticado, brother ');

		},
		data: JSON.stringify(credentials) 
		
	});
}
