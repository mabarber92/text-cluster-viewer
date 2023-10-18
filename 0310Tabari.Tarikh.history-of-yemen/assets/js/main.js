//Fetch data from the index
// import data from "./index.json" assert { type: 'json' };            


//Create the sidebar html
let sideBarLinks = buildMsContents()


//On page load - load the main json and run tasks
window.onload = (event) => {
    
    let queryString = window.location.search.split("?=ms")[1];
    let dataPath = "./index.json"
    get(dataPath).then(function(response) {
        var mainData = JSON.parse(response);
        buildOnPageLoad(queryString, mainData);
    });

    // Use the pre-prepocessed content-page html to populate the sidebar
    let sideBar = document.getElementById("ms-contents-page")
    sideBar.appendChild(sideBarLinks)

    // When page has loaded - run requisite functions
    // clusterSelector();
    titlePopulator();
    // selectAll();
    
    // Check the local storage to see if the panel was open in the previous view
    // If it is open it on the page load
    if (localStorage['panelOpen'] === 'true') {
        
        openPanel()
    };

    };

// Set the currentMs as first ms or  into the box
function buildOnPageLoad (queryString, data) {
    if (queryString === undefined) {
        let params = new URLSearchParams(window.location.search);
        params.set('', `ms${data[0].ms}`);
        window.location.search = params;
        let queryString = window.location.search.split("?=ms")[1];
        
    };
    
    let msData = data.filter(
        function(data) {return data.ms == queryString}
    );
    if (msData[0] === undefined) {
        // Consider adding error message before defaulting to first available page
        let params = new URLSearchParams(window.location.search);
        params.set('', `ms${data[0].ms}`);
        window.location.search = params;
        let queryString = window.location.search.split("?=ms")[1];
    } else {
        fillMsBoxes(msData[0], data);
    };

}


//Function to create the contents page
function buildMsContents () {        
    let contentsBox = document.createElement("div");
    let dataPath = "./index.json";

    get(dataPath).then(function(response) {
        var data = JSON.parse(response);
        data.forEach(msEntry => {
        let msListItem = document.createElement("li");
        let linkText = `ms${msEntry.ms} - ${msEntry.cls_count} Clusters`;
        let linkHref = `?=ms${msEntry.ms}`;
        let link = document.createElement("a");
        link.href = linkHref;
        linkText = document.createTextNode(linkText);
        link.appendChild(linkText);
        msListItem.appendChild(link);
        contentsBox.appendChild(msListItem);
        });

    });

    
    return contentsBox
};

//Function to set text as content of box - takes just the text
function fillMsBoxes(msData, data) {
    
    let msBox = document.getElementById('ms-container');    
    msBox.innerHTML = msData.text;

    let msName = document.getElementById('ms-no');
    msName.innerHTML = `ms${msData.ms}`;

    let clusterCountBox = document.getElementById('cluster-count');
    clusterCountBox.innerHTML = `Number of Clusters: ${msData.cls_count}`

    // let clusterOptions = document.getElementById('cluster-selector');
    // clusterOptions.innerHTML = "";
    // for (let i=0; i < msData.cls.length; i++) {
    //     let clusterData = msData.cls[i];
        
    //     let optionHtml = document.createElement("option")
    //     optionHtml.value = `./${msData.cl_json}-${clusterData.cl_id}`;
    //     let optionText = document.createTextNode(`${clusterData.cl_id}-(${clusterData.ms_count} ms)`)
    //     optionHtml.appendChild(optionText)
                        
    //     clusterOptions.appendChild(optionHtml);
    // };
    createClusterCard(msData);
    
    
    let nextMs = msData.ms + 1;
    let nextMsData = data.filter(
        function(data) {return data.ms == nextMs});
    
    let prevMs = msData.ms - 1;
    let prevMsData = data.filter(
    function(data) {return data.ms == prevMs});

    if (nextMsData.length === 1) {                    
        let nextButton = document.getElementById('next-button');
        nextButton.href = `?=ms${nextMs}`;
    };

    if (prevMsData.length === 1) {
        
        let backButton = document.getElementById('back-button');
        backButton.href = `?=ms${prevMs}`;
    };
    

    
};



// Function handling a cluster selection
function clusterSelector () {
    let clusterSelector = document.getElementById('cluster-selector')
    console.log(clusterSelector)

    clusterSelector.onchange = (event) => {                
        console.log(event)
        handleSelection()
    };
};


function handleSelection() {    
    const selected = document.querySelectorAll('#cluster-selector option:checked')
    const multiSelect = Array.from(selected).map(el => el.value);
    let booksContainer = document.getElementById("cl-book-list");
    let containOption1 = document.getElementById("pairs-dropdown-1")
    let containOption2 = document.getElementById("pairs-dropdown-2")
    booksContainer.innerHTML = ""
    containOption1.innerHTML = "<option>choose a book</option>"
    containOption2.innerHTML = "<option>choose a book</option>"

    multiSelect.forEach( clusterItem => {
        let selectedValue = clusterItem.split("-");
        let cluster = Number(selectedValue[1]);
        let jsonFile = selectedValue[0];

        console.log(jsonFile);
        
        // let clusterData = getClusterData(jsonFile)
        get(jsonFile).then(function(response) {
            var clusterData = JSON.parse(response);
            let selectedCluster = clusterData.filter(
                function(data) {return data.cl_id === cluster})
            
            populateBooks(selectedCluster[0].texts, jsonFile, cluster);
            return response
            
        });
    })
    

};


function createClusterCard (data) {
    let clusterContainer = document.getElementById("cl-book-list");
    let jsonPath = data.cl_json;
    console.log(data.cls)
    let sortedCls = data.cls.sort((a, b) => 
        a.ms_count - b.ms_count
    )
    console.log(sortedCls)
    sortedCls.forEach(cl =>{
        let colDiv = document.createElement('div');
        colDiv.setAttribute("class", "col");
        let cardDiv = document.createElement('div');
        cardDiv.setAttribute("class", "card");
        colDiv.appendChild(cardDiv);
        let cardTitle = document.createElement('div');
        cardTitle.setAttribute("class", "card-header pt-1 pb-1");
        titleText = document.createTextNode(`${cl.cl_id} - ${cl.ms_count} Ms`);
        cardTitle.appendChild(titleText);
        cardDiv.appendChild(cardTitle);
        let cardBody = document.createElement("ul");
        cardBody.setAttribute("class", "list-group list-group-flush");        
        get(jsonPath).then(
            function(response) {
                var clusterData = JSON.parse(response);                
                let selectedCluster = clusterData.filter(
                    function(data) {return data.cl_id === cl.cl_id}
                );
                populateBooks(selectedCluster[0].texts, jsonPath, cl.cl_id)
                
                selectedCluster[0].texts.forEach(text => {
                    cardRow = document.createElement("li");
                    cardRow.setAttribute("class", "list-group-item pt-0 pb-0")
                    cardRow.innerHTML = `${text.ms_id}
                    <a onClick="populateTextContainer('${jsonPath}!${cl.cl_id}!${text.ms_id}','text-container-1', 'title-1', event=false)"> 
                        <i class="bi bi-1-square"> </i>
                    </a>
                    <a onClick="populateTextContainer('${jsonPath}!${cl.cl_id}!${text.ms_id}','text-container-2', 'title-2', event=false)"> 
                        <i class="bi bi-2-square"></i>
                    </a>
                    `
                    cardBody.appendChild(cardRow)
                });
            }
        );
        cardDiv.appendChild(cardBody);
        clusterContainer.appendChild(colDiv);
        }
    );

}

function titlePopulator () {
    let msSelectorOne = document.getElementById('pairs-dropdown-1');
    msSelectorOne.onchange = (event) => {
        console.log(event)
        populateTextContainer(event, "text-container-1", "title-1");
    };

    let msSelectorTwo = document.getElementById('pairs-dropdown-2');
    msSelectorTwo.onchange = (event) => {
        populateTextContainer(event, "text-container-2", "title-2");
    };
};


function populateTextContainer (input, container, titleContainer, event=true) {
    
    if (event === true) {
        var selectedValue = input.target.value.split("!");
    } else {
        var selectedValue = input.split("!");
    };
    
    console.log(selectedValue)
    let msId = selectedValue[2];
    let clusterId = Number(selectedValue[1]);
    let jsonFile = selectedValue[0];

    get(jsonFile).then(function(response) {
        var clusterData = JSON.parse(response);
        
        let selectedCluster = clusterData.filter(
            function(data) {return data.cl_id === clusterId});
            console.log(selectedCluster)
        let selectedMs = selectedCluster[0].texts.filter(
            function(data) {return data.ms_id === msId}
        );
        
        let htmlContainer = document.getElementById(container);                
        htmlContainer.innerHTML = selectedMs[0].text;
        
        let titleHtmlContainer = document.getElementById(titleContainer);
        titleHtmlContainer.innerHTML = ""
        let header = document.createElement("h5");
        let headerText = document.createTextNode(msId);
        header.appendChild(headerText);
        titleHtmlContainer.appendChild(header)

        return response

    });
};

function populateBooks (bookList, jsonFile, cluster) {
    // let booksContainer = document.getElementById("cl-book-list");
    let containOption1 = document.getElementById("pairs-dropdown-1")
    let containOption2 = document.getElementById("pairs-dropdown-2")
    // booksContainer.innerHTML = ""
    // containOption1.innerHTML = "<option>choose a book</option>"
    // containOption2.innerHTML = "<option>choose a book</option>"
    bookList.forEach(book => {
        let listItem = document.createElement("li");
        let optionItem = document.createElement("option");
        let optionItem2 = optionItem.cloneNode();
        let listText = document.createTextNode(book.ms_id);
        listItem.appendChild(listText);

        optionItem.value = `${jsonFile}!${cluster}!${book.ms_id}`;
        optionItem2.value = `${jsonFile}!${cluster}!${book.ms_id}`;
        optionItem.appendChild(listText.cloneNode());
        optionItem2.appendChild(listText.cloneNode())
        
        


        // booksContainer.appendChild(listItem);
        containOption2.appendChild(optionItem2);
        containOption1.appendChild(optionItem);
        
        
    }); 
};

//Select all function
function selectAll () {
    let selectAllButton = document.getElementById("select-all")

    selectAllButton.onclick = () => {
        let selectBox = document.getElementById("cluster-selector")
        for (var i = 0; i < selectBox.options.length; i++) { 
            selectBox.options[i].selected = "true";    
        };
        handleSelection()
    };
}






// Function for fetching the json
function get(url) {
    // Return a new promise.
    return new Promise(function(resolve, reject) {
        // Do the usual XHR stuff
        var req = new XMLHttpRequest();
        req.open('GET', url);

        req.onload = function() {
        // This is called even on 404 etc
        // so check the status
        if (req.status == 200) {
            // Resolve the promise with the response text
            resolve(req.response);
        }
        else {
            // Otherwise reject with the status text
            // which will hopefully be a meaningful error
            reject(Error(req.statusText));
        }
        };

        // Handle network errors
        req.onerror = function() {
        reject(Error("Network Error"));
        };

        // Make the request
        req.send();
    });
    };

    function getJSON(url) {
        return get(url).then(JSON.parse);
        }
