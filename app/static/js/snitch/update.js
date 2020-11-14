var SnitchDNSUpdate = {
    updateUrl: '',
    currentVersion: '',

    init: function(updateUrl, currentVersion) {
        this.updateUrl = updateUrl;
        this.currentVersion = currentVersion;
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
                (result && result.content)
                    ? SnitchDNSUpdate.checkVersion(SnitchDNSUpdate.cleanVersion(result.content))
                    : SnitchDNSUpdate.showMessage('Could not fetch latest version', 'text-danger');
            },
            error: function(result) {
                SnitchDNSUpdate.showMessage('Could not fetch latest version', 'text-danger');
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

    cleanVersion: function(version) {
        return atob(version)
            .replace('__version__', '')
            .replace('=', '')
            .replace(/'/g, '')
            .trim();
    },

    checkVersion: function(latestVersion) {
        (latestVersion === SnitchDNSUpdate.currentVersion)
            ? SnitchDNSUpdate.showMessage('You have the latest and greatest!', '')
            : SnitchDNSUpdate.showMessage('There is a new version!', 'text-info');
    }
};
