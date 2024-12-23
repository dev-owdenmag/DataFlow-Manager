function deleteEntry(clientId) {
    fetch(`/delete/${clientId}`, {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error deleting entry.');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(data.message);
            location.reload(); // Refresh the page to reflect the updated details
        }
    })
    .catch(error => {
        console.error(error);
        alert('Error deleting entry. Please try again.');
    });
}
