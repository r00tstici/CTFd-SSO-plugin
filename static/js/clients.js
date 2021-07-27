function deleteSelectedOAuthClients(_event) {
    let clientIDs = $("input[data-client-id]:checked").map(function () {
        return $(this).data("client-id");
    });
    let target = clientIDs.length === 1 ? "client" : "clients";

    CTFd.ui.ezq.ezQuery({
        title: "Delete clients",
        body: `Are you sure you want to delete ${clientIDs.length} ${target}?`,
        success: function () {
            const reqs = [];
            for (var clientID of clientIDs) {
                reqs.push(
                    CTFd.fetch(`/admin/sso/client/${clientID}`, {
                        method: "DELETE"
                    })
                );
            }
            Promise.all(reqs).then(_responses => {
                window.location.reload();
            });
        }
    });
}

$(() => {
    $("#oauth-clients-delete-button").click(deleteSelectedOAuthClients);
});
