var SnitchEmailRecipients = {
    init: function(recipients) {
        this.bindAddRecipient();
        this.bindDeleteRecipient();
        this.bindSubmit();
        this.groupAddRecipients(recipients);
    },

    bindAddRecipient: function() {
        $('#add-recipient').click(function() {
            SnitchEmailRecipients.addRecipient($('#recipient').val());
            return false;
        });

        $('#recipient').on('keypress', function(e) {
            if (e.keyCode == 13) {
                SnitchEmailRecipients.addRecipient($('#recipient').val());
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        });
    },

    bindDeleteRecipient: function() {
        $('.recipient-list').on('click', 'a.delete-recipient', function() {
            SnitchEmailRecipients.deleteRecipient(this);
            return false;
        });
    },

    bindSubmit: function() {
        $('.save-button').click(function() {
            return SnitchEmailRecipients.submitForm();
        });
    },

    submitForm: function() {
        var recipients = this.getRecipients();
        for (var i = 0; i < recipients.length; i++) {
            var template = $('.recipient-hidden-input').clone();
            $(template).removeClass('recipient-hidden-input').val(recipients[i]);
            $('.recipient-form').append(template);
        }
        $('.recipient-hidden-input').remove();

        return true;
    },

    deleteRecipient: function(obj) {
        $(obj).closest('li').remove();
    },

    addRecipient: function(recipient) {
        recipient = recipient.trim().toLowerCase();
        if (!this.isEmailValid(recipient)) {
            alert('Invalid e-mail address');
            return false;
        } else if (this.isDuplicate(recipient)) {
            alert('E-mail recipient already exists');
            return false;
        }

        var template = $('.recipient-template').clone();
        template.find('span.recipient-email').text(recipient);
        template.removeClass('hidden').removeClass('recipient-template');

        $('.recipient-list').append(template);
        $('#recipient').val('').focus();

        this.showSave();
    },

    isDuplicate: function(email) {
        email = email.trim().toLowerCase();
        recipients = this.getRecipients();
        return ($.inArray(email, recipients) >= 0);
    },

    getRecipients: function() {
        recipients = [];
        $('.recipient-list li span.recipient-email').each(function() {
            var e = $(this).text().trim().toLowerCase();
            if (e.length > 0 && SnitchEmailRecipients.isEmailValid(e)) {
                recipients.push(e);
            }
        });
        return recipients;
    },

    showSave: function() {
        $('.save-button').removeClass('d-none');
    },

    isEmailValid: function(email) {
        // Why not - https://stackoverflow.com/a/46181
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    },

    groupAddRecipients: function(recipients) {
        for (var i = 0; i < recipients.length; i++) {
            if (this.isEmailValid(recipients[i])) {
                this.addRecipient(recipients[i]);
            }
        }
    }
};