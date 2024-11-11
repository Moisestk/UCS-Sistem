const pass = document.getElementById("password")
const parrafo = document.getElementById("warnings")
const form = document.getElementById("form")

form.addEventListener("submit", e=>{
    e.preventDefault()
    let warnings = ""
    let entrar = false
    parrafo.innerHTML = ""

    if(pass.value.length < 8){
        warnings += `La contraseña no es valida <br>`
        entrar = true
    }

    if(entrar){
        parrafo.innerHTML = warnings
    }
    
    else{
        parrafo.innerHTML = "Enviando"
    }
        
    })