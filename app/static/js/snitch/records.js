var SnitchDNSRecords = {
    init: function(properties) {
        this.bindType();
        if (typeof properties === 'undefined') {
            properties = {};
        }

        $('#type').trigger('change');
        this.setValues(properties);
    },

    getType: function() {
        return $('#type').val();
    },

    bindType: function() {
        $('#type').change(function() {
            SnitchDNSRecords.buildUI($(this).val());
        });
    },

    setValues: function(properties) {
        switch (this.getType()) {
            case 'NS':
            case 'CNAME':
            case 'PTR':
            case 'DNAME':
                $('#name').val(properties['name']);
                break;
            case 'A':
            case 'AAAA':
                if ('address' in properties) {
                    $('#address').val(properties['address']);
                }
                break;
            case 'SOA':
                ['mname', 'rname', 'serial', 'refresh', 'retry', 'expire', 'minimum'].forEach((n) => {
                    $('#' + n).val(properties[n]);
                });
                break;
            case 'SRV':
                ['priority', 'weight', 'port', 'target'].forEach((n) => {
                    $('#' + n).val(properties[n]);
                });
                break;
            case 'NAPTR':
                ['order', 'preference', 'flags', 'service', 'regexp', 'replacement'].forEach((n) => {
                    $('#' + n).val(properties[n]);
                });
                break;
            case 'AFSDB':
                ['subtype', 'hostname'].forEach((n) => {
                    $('#' + n).val(properties[n]);
                });
                break;
            case 'RP':
                ['mbox', 'txt'].forEach((n) => {
                    $('#' + n).val(properties[n]);
                });
                break;
            case 'HINFO':
                ['cpu', 'os'].forEach((n) => {
                    $('#' + n).val(properties[n]);
                });
                break;
            case 'MX':
                ['name', 'preference'].forEach((n) => {
                    $('#' + n + '2').val(properties[n]);
                });
                break;
            case 'SSHFP':
                ['algorithm', 'fingerprint_type', 'fingerprint'].forEach((n) => {
                    $('#' + n).val(properties[n]);
                });
                break;
            case 'TXT':
            case 'SPF':
                ['data'].forEach((n) => {
                    $('#' + n).val(properties[n]);
                });
                break;
            case 'TSIG':
                ['algorithm', 'timesigned', 'fudge', 'original_id', 'mac', 'other_data'].forEach((n) => {
                    c = (n == 'algorithm') ? 'algorithm2' : n;
                    $('#' + c).val(properties[n]);
                });
                break;
        }
    },

    getRecordGroup: function(recordType) {
        var recordMapping = {
            'NS': 'record-group-1',
            'CNAME': 'record-group-1',
            'PTR': 'record-group-1',
            'DNAME': 'record-group-1',
            'A': 'record-group-2',
            'AAAA': 'record-group-2',
            'SOA': 'record-group-3',
            'SRV': 'record-group-4',
            'NAPTR': 'record-group-5',
            'AFSDB': 'record-group-6',
            'RP': 'record-group-7',
            'HINFO': 'record-group-8',
            'MX': 'record-group-9',
            'SSHFP': 'record-group-10',
            'TXT': 'record-group-11',
            'SPF': 'record-group-11',
            'TSIG': 'record-group-12'
        };

        return (recordType in recordMapping) ? recordMapping[recordType] : false;
    },

    buildUI: function(selectedType) {
        // Hide all.
        $('.record-group').addClass('d-none');
        if (selectedType == '') {
            return true;
        }

        group = this.getRecordGroup(selectedType);
        if (group === false) {
            alert('Invalid DNS Record Type');
            return false;
        }

        // And show the one we want.
        $('.' + group).removeClass('d-none');
        return true;
    }
};