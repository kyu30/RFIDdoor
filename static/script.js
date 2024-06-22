document.addEventListener('DOMContentLoaded', function(){
    fetchWhitelist();
});

document.getElementById('addForm').addEventListener('submit', function(event){
    event.preventDefault();
    const uid = document.getElementById('uid').value;
    const name = document.getElementById('name').value;
    const access = document.getElementById('access').value;
    addEntry(uid, name, accessLevel)
})

function fetchWhitelist(){
    fetch('/get_whitelist')
    .then(response => response.json())
    .then(data => {
        console.log(data);
        const whitelist = document.getElementById('whitelist');
        whitelist.innerHTML = '';
        data.forEach(entry => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${entry.UID}</td>
                <td>${entry.User}</td>
                <td>${entry.Permission}</td>
                <td>${entry.LastUsed}</td>
                <td><button onclick = "deleteEntry('${entry.UID}')">Delete</button></td>
                `;
                whitelist.appendChild(row);
        });
    });
}

function addEntry(uid, name, access){
    fetch('/add_entry', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ uid, name, accessLevel })
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success'){
            fetchWhitelist();
        } else{
            alert ('Failed to add entry');
        }
    });
}

function deleteEntry(uid){
    fetch('/delete_entry', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({uid})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            fetchWhitelist();
        } else {
            alert('Failed to delete entry')
        }
    });
}