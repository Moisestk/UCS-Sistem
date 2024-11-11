const form = dodument.getElementById('form')
const titulo = document.getElementById('titulo')
const autores = document.getElementById('autores')
const cedula = document.getElementById('cedula')
const descripcion = document.getElementById('descripcion')
const estado = document.getElementById('estado')
const parroquia = document.getElementById('parroquia')
const municipio = document.getElementById('municipio')
const nombre = document.getElementById('nombre')
const palabras = document.getElementById('palabras')
const tutor = document.getElementById('tutor')
const tutor_metodologico = document.getElementById('tutor_metodologico')




form.addEventListener("submit", e=>{
    e.preventDefault()

    let warnings = ""
    let entrar = false


    if(titulo.value.length <10){
        warnings += `Coloque el titulo completo <br>`
        entrar = true
    }

    if(descripcion.value.length <6){
        warnings += `Coloque una descripcion clara <br>`
        entrar = true
    }

    if(titulo.value.length > 10){
        warnings += `Recuerda colocar solo el nombre y el apellido <br>`
        entrar = true
    }


})