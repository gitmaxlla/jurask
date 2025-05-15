const answer_text = document.getElementById("answer-text");
const status_message =  document.getElementById("status");

let nowDragging = null;
let nowResizing = null;
let windows = [];

document.getElementById("submit").onclick = () => {
    send_query();
}

document.getElementById("input").oninput = function() {
    var reference_wrapper = document.getElementById("input-measure-wrapper");
    var reference = document.getElementById("input-width-measure");

    reference_wrapper.style.maxWidth = this.offsetWidth + "px";
    reference.innerText = this.innerText;
    this.style.width = reference.offsetWidth + 20 + "px";
}

async function send_query() {
    const references = document.getElementById("references");

    answer_text.innerText = '';
    references.innerHTML = '';

    status_message.classList.remove("none");
    input = document.getElementById("input").innerText;

    const progressBar = document.getElementById("main-separator")
    progressBar.classList.add("progress-bar-animation");

    fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json;charset=utf-8"
        },
        body: JSON.stringify({"contents": input})
    }).then((response => response.json())).then(answer => {
        display_response(answer);
        progressBar.classList.remove("progress-bar-animation");
    })
}

function display_referenced_documents(references) {
    for (const [reference_num, data] of Object.entries(references)) {
        const reference_name = document.createElement("button");
        reference_name.className = "referenced-article-btn";
        reference_name.innerText = reference_num + ". " + data.law + ". " + data.chapter;

        const reference_text = document.createElement("div");
        reference_text.className = "referenced-article-text none";
        reference_text.innerText = "123";
        
        reference_name.addEventListener("click", function() {
            this.classList.toggle("is-expanded");
            var text = this.nextElementSibling;
        
            if (text.classList.contains("none")) {
                text.classList.remove("none")
            } else {
                text.classList.add("none")
            }
        });

        globalThis.references.appendChild(reference_name);
        globalThis.references.appendChild(reference_text);
    }
}

function build_links(string, references) {
    result = ""
    numbers = string.split(',')
    for (const num_str of numbers) {
        num = parseInt(num_str.trim())
        reference = references[num]
        tooltip_text = reference.law + ". " + reference.chapter + ". " + reference.article;
        result += "<div class='tooltip'>"
        result += "<a class='reference " + "fragment_" + num + "'>" + num + "</a><br>"
        result += "<span class='tooltip-text'>" + tooltip_text + "</span></div>, "
    }
    return result.slice(0, result.length - 2)
}

function create_window(title) {
    let window = document.createElement("div");
    windows.push(window);
    window.classList.add("window");

    let windowHeader = document.createElement("div");
    windowHeader.classList.add("window-header");
    windowHeader.innerText = title;

    window.appendChild(windowHeader);

    windowHeader.onmousedown = (e) => {
        nowDragging = window;
        for (const element of windows) {
            if (element != this){
                element.style.zIndex = 2;
            }
        }

        window.style.zIndex = 3;
    }

    document.onmouseup = (e) => {
        nowDragging = null;
        nowResizing = null;
    }

    const windowCloseBtn = document.createElement("div");
    windowCloseBtn.classList.add("window-close-btn");

    const closeIcon = document.createElement("img");
    closeIcon.src = "jurask-close.svg";
    windowCloseBtn.appendChild(closeIcon);

    windowCloseBtn.onclick = (e) => {
        e.target.parentNode.parentNode.parentNode.remove();
    }

    windowHeader.appendChild(windowCloseBtn);


    let windowContent = document.createElement("p");
    windowContent.classList.add("window-content")

    window.appendChild(windowContent);

    let resizeAreaDiv = document.createElement("div");
    resizeAreaDiv.classList.add("resize-area");
    let resizeArea = document.createElement("div");

    resizeArea.classList.add("resize-icon");

    const resizeIcon = document.createElement("img");
    resizeIcon.src = "jurask-resize.svg";
    resizeArea.appendChild(resizeIcon);

    resizeArea.onmousedown = (e) => {
        nowResizing = window;
        answer_text.style['userSelect'] = 'none';
    }

    document.getElementsByTagName("main")[0].onmousemove = (e) => {
        if (nowResizing) {
            nowResizing.style['width'] = nowResizing.clientWidth - 39 + e.movementX + "px";
            nowResizing.style['height'] = nowResizing.clientHeight - 30 + e.movementY + "px";
        }

        if (nowDragging) {            
            nowDragging.style['left'] = (nowDragging.offsetLeft + e.movementX) + "px";
            nowDragging.style['top'] = (nowDragging.offsetTop + e.movementY) + "px";
        }
    }

    resizeAreaDiv.appendChild(resizeArea);

    window.style['width'] = window.clientWidth + "px";
    window.style['height'] = window.clientHeight + "px";
    window.appendChild(resizeAreaDiv);


    fetch("/ref", {
        method: "POST",
        headers: {
            "Content-Type": "application/json;charset=utf-8"
        },
        body: JSON.stringify({"document": title.split('.')[0], "name": title.substring(title.indexOf('.') + 2)})
    }).then((response => response.json())).then(answer => {
        windowContent.innerText = answer['content'];
        document.getElementsByTagName("main")[0].appendChild(window)
    })
}

function display_response(result_answer) {
    const status = result_answer[0];
    if (status == "OK") {
        const answer = result_answer[1].final_answer;
        const references = result_answer[1].used_references;

        status_message.classList.add("none");
        document.getElementById("answer").classList.remove("hidden");
        let result = "";
    
        for (let i = 0; i < answer.length; i++) {
            char = answer.charAt(i);
    
            if (char == '[') {
                result += char
                inside_brackets = ""
    
                while (answer.charAt(i + 1) != ']') {
                    i += 1
                    char = answer.charAt(i);
                    inside_brackets += char
                }
    
    
                links_html = build_links(inside_brackets, references);
                result += links_html;
            } else {
                result += char;
            }
    
            answer_text.innerHTML = result
        }
    
        for (const [reference_num, data] of Object.entries(references)) {
            elements = document.getElementsByClassName("fragment_" + reference_num);
            for (const element of elements) {
                element.onclick = (e) => {
                    let title = e.target.nextSibling.nextSibling.innerText;
                    create_window(title);
                };
                element.onmouseover = (e) => {
                    tooltip_side = e.clientX < (window.innerWidth / 2);
                    tooltip_text = e.target.nextSibling.nextSibling;
                    if (tooltip_side) {
                        tooltip_text.style['left'] = "1rem";
                        tooltip_text.style['right'] = "auto";
                    } else {
                        tooltip_text.style['right'] = "1rem";
                        tooltip_text.style['left'] = "auto";
                    }
                };
            }
        }
    } else if (status == "TOO COMPLEX") {
        status_message.innerText = "К сожалению, запрос оказался слишком сложным для текущей версии системы. " +
                                   "Пожалуйста, упростите его или разделите на несколько."
    } else if (status == "IRRELEVANT") {
        status_message.innerText = "Похоже, запрос не относится к сфере знаний системы. Попробуйте конкретизировать его " +
                                   "либо обратиться к другим источникам информации."
    } else {
        status_message.innerText = "В результате обработки запроса произошла ошибка. Попробуйте повторить ваш запрос к системе позже."
    }

}
