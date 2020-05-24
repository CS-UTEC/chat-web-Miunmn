function get_current(){
    console.log("Deja traigo el usuario logueado: ");
    $.getJSON("/current", function(data)
    {
        console.log(data['username'])
        var div = '<div><span> Username </span></div>' ;
        div = div.replace('username', data['username']);
        $('#contacts').append(div);  
        get_users();        
    });
}

function saludar(name){
alert ("Hello" + name);
}
function get_users(){
        console.log("Deja traigo el usuario logueado: ");
        $.getJSON("/users", function(data){
        let i =0;
        $.each(data, function(){
                var div = '<div onclick = "saludar (\'p_name\')" ><span> username </span></div>' ;
                div = div.replace("username", data[i]['username']);
                div = div.replace("p_name", data[i]['username']);
                $('#contacts').append(div);
                i=i+1;
                  
            })
         
        });

}
