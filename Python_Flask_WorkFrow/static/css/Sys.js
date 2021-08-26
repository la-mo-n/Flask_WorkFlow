


document.getElementById("btnsubmit").onclick = function(){
	
    var result = window.confirm("確定します。よろしいでしょうか？");
    
    if( result ) {
        document.getElementById("flg_yes_no").value = "YES";    
        alert("確定しました");        
    }
    else {
        document.getElementById("flg_yes_no").value = "NO";
        alert("キャンセルしました");
        return false;
    }

}




document.getElementById("btndlt").onclick = function(){
	
    var result = window.confirm("削除します。よろしいでしょうか？");
    
    if( result ) {
        document.getElementById("flg_yes_no").value = "YES";    
        alert("削除しました");        
    }
    else {
        document.getElementById("flg_yes_no").value = "NO";
        alert("キャンセルしました");
    }

}