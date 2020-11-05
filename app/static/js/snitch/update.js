var SnitchDNSUpdate = {
    updateUrl: '',
    currentCommit: '',

    init: function(updateUrl, currentCommit) {
        this.updateUrl = updateUrl;
        this.currentCommit = currentCommit;
        this.bindButton();
    },

    bindButton: function() {
        $('#check_for_updates').click(function() {
            SnitchDNSUpdate.check();
            return false;
        });
    },

    check: function() {
        $('#check_for_updates').text('please wait...');
        $.ajax({
            url: SnitchDNSUpdate.updateUrl,
            cache: false,
            type: 'get',
            success: function(result) {
                (result && result.object && result.object.sha)
                    ? SnitchDNSUpdate.checkVersion(result.object.sha)
                    : SnitchDNSUpdate.showMessage('Could not fetch latest commit', 'text-danger');
            },
            error: function(result) {
                SnitchDNSUpdate.showMessage('Could not fetch latest commit', 'text-danger');
            }
        });
    },

    showMessage: function(message, textClass) {
        $('#update_col_right').html('');
        $('.update_text_left').text(message);
        if (textClass.length > 0) {
            $('.update_text_left').addClass(textClass);
        }
    },

    checkVersion: function(latestCommit) {
        latestCommit = latestCommit.substr(0, 7);
        (latestCommit === SnitchDNSUpdate.currentCommit)
            ? SnitchDNSUpdate.showMessage('You have the latest and greatest!', '')
            : SnitchDNSUpdate.showMessage('There is a new version!', 'text-info');
    }
};
