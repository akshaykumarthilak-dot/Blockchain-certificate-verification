// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract CertificateAuthentication {

    // Certificate structure
    struct Certificate {
        string certificateId;
        string certificateType; // "educational", "professional", "achievement", "license", etc.
        string holderName;
        string institutionName;
        string qualificationName;
        string imageHash;
        address issuer;
        address currentHolder;
        uint256 issuedAt;
        uint256 expiryDate; // 0 if no expiry
        bool exists;
        bool isValid;
        bool isRevoked;
    }

    // Transfer/Transfer history structure
    struct Transfer {
        address from;
        address to;
        uint256 timestamp;
        string transferType; // "issue", "transfer", "revoke"
    }

    // Verification log structure
    struct VerificationLog {
        address verifier;
        uint256 timestamp;
        bool isValid;
    }

    // Mappings
    mapping(string => Certificate) public certificates; // certificateId => Certificate
    mapping(string => Transfer[]) public certificateTransfers; // certificateId => Transfer history
    mapping(string => VerificationLog[]) public verificationLogs; // certificateId => Verification history
    mapping(address => bool) public authorizedIssuers; // Authorized addresses that can issue certificates
    mapping(string => string) public qrCodeToCertificate; // QR code hash => certificateId

    address public admin;
    string[] public certificateIds;

    // Events
    event CertificateIssued(string indexed certificateId, string holderName, string institutionName, address issuer, uint256 timestamp);
    event CertificateTransferred(string indexed certificateId, address indexed from, address indexed to, uint256 timestamp);
    event CertificateVerified(string indexed certificateId, address indexed verifier, bool isValid, uint256 timestamp);
    event CertificateRevoked(string indexed certificateId, address indexed revoker, uint256 timestamp);
    event IssuerAuthorized(address indexed issuer, uint256 timestamp);
    event IssuerRevoked(address indexed issuer, uint256 timestamp);
    event QRCodeLinked(string indexed certificateId, string qrHash, uint256 timestamp);

    // Modifiers
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    modifier onlyAuthorizedIssuer() {
        require(authorizedIssuers[msg.sender] || msg.sender == admin, "Only authorized issuers can perform this action");
        _;
    }

    modifier certificateExists(string memory _certificateId) {
        require(certificates[_certificateId].exists, "Certificate does not exist");
        _;
    }

    constructor() {
        admin = msg.sender;
        authorizedIssuers[msg.sender] = true; // Admin is also an issuer
    }

    // Authorize an issuer to issue certificates
    function authorizeIssuer(address _issuer) public onlyAdmin {
        require(_issuer != address(0), "Invalid address");
        authorizedIssuers[_issuer] = true;
        emit IssuerAuthorized(_issuer, block.timestamp);
    }

    // Revoke issuer authorization
    function revokeIssuer(address _issuer) public onlyAdmin {
        require(_issuer != admin, "Cannot revoke admin");
        authorizedIssuers[_issuer] = false;
        emit IssuerRevoked(_issuer, block.timestamp);
    }

    // Issue a new certificate
    function issueCertificate(
        string memory _certificateId,
        string memory _certificateType,
        string memory _holderName,
        string memory _institutionName,
        string memory _qualificationName,
        string memory _imageHash,
        uint256 _expiryDate
    ) public onlyAuthorizedIssuer returns (bool) {
        require(!certificates[_certificateId].exists, "Certificate already exists");
        require(bytes(_certificateId).length > 0, "Certificate ID cannot be empty");

        certificates[_certificateId] = Certificate({
            certificateId: _certificateId,
            certificateType: _certificateType,
            holderName: _holderName,
            institutionName: _institutionName,
            qualificationName: _qualificationName,
            imageHash: _imageHash,
            issuer: msg.sender,
            currentHolder: msg.sender,
            issuedAt: block.timestamp,
            expiryDate: _expiryDate,
            exists: true,
            isValid: true,
            isRevoked: false
        });

        certificateIds.push(_certificateId);

        // Record initial transfer (issue)
        certificateTransfers[_certificateId].push(Transfer({
            from: address(0),
            to: msg.sender,
            timestamp: block.timestamp,
            transferType: "issue"
        }));

        emit CertificateIssued(_certificateId, _holderName, _institutionName, msg.sender, block.timestamp);
        return true;
    }

    // Link QR code to certificate
    function linkQRCode(string memory _certificateId, string memory _qrHash)
        public
        onlyAuthorizedIssuer
        certificateExists(_certificateId)
        returns (bool)
    {
        require(bytes(_qrHash).length > 0, "QR hash cannot be empty");
        require(bytes(qrCodeToCertificate[_qrHash]).length == 0, "QR code already linked to another certificate");

        qrCodeToCertificate[_qrHash] = _certificateId;
        emit QRCodeLinked(_certificateId, _qrHash, block.timestamp);
        return true;
    }

    // Transfer certificate ownership
    function transferCertificate(string memory _certificateId, address _newHolder)
        public
        certificateExists(_certificateId)
        returns (bool)
    {
        require(certificates[_certificateId].currentHolder == msg.sender, "Only current holder can transfer");
        require(_newHolder != address(0), "Invalid new holder address");
        require(_newHolder != msg.sender, "Cannot transfer to yourself");
        require(!certificates[_certificateId].isRevoked, "Cannot transfer revoked certificate");

        address previousHolder = certificates[_certificateId].currentHolder;
        certificates[_certificateId].currentHolder = _newHolder;

        certificateTransfers[_certificateId].push(Transfer({
            from: previousHolder,
            to: _newHolder,
            timestamp: block.timestamp,
            transferType: "transfer"
        }));

        emit CertificateTransferred(_certificateId, previousHolder, _newHolder, block.timestamp);
        return true;
    }

    // Revoke certificate
    function revokeCertificate(string memory _certificateId)
        public
        certificateExists(_certificateId)
        returns (bool)
    {
        require(certificates[_certificateId].issuer == msg.sender || msg.sender == admin, "Only issuer or admin can revoke");
        require(!certificates[_certificateId].isRevoked, "Certificate already revoked");

        certificates[_certificateId].isRevoked = true;
        certificates[_certificateId].isValid = false;

        certificateTransfers[_certificateId].push(Transfer({
            from: certificates[_certificateId].currentHolder,
            to: address(0),
            timestamp: block.timestamp,
            transferType: "revoke"
        }));

        emit CertificateRevoked(_certificateId, msg.sender, block.timestamp);
        return true;
    }

    // Verify certificate authenticity and validity
    function verifyCertificate(string memory _certificateId)
        public
        certificateExists(_certificateId)
        returns (bool isValid)
    {
        Certificate memory certificate = certificates[_certificateId];

        // Check if certificate is revoked
        if (certificate.isRevoked) {
            isValid = false;
        }
        // Check if certificate has expired
        else if (certificate.expiryDate > 0 && block.timestamp > certificate.expiryDate) {
            isValid = false;
        }
        else {
            isValid = certificate.isValid;
        }

        verificationLogs[_certificateId].push(VerificationLog({
            verifier: msg.sender,
            timestamp: block.timestamp,
            isValid: isValid
        }));

        emit CertificateVerified(_certificateId, msg.sender, isValid, block.timestamp);
        return isValid;
    }

    // Verify by QR code hash
    function verifyByQRCode(string memory _qrHash) public returns (bool isValid, string memory certificateId) {
        certificateId = qrCodeToCertificate[_qrHash];
        require(bytes(certificateId).length > 0, "QR code not linked to any certificate");

        isValid = verifyCertificate(certificateId);
        return (isValid, certificateId);
    }

    // Get certificate details
    function getCertificate(string memory _certificateId)
        public
        view
        certificateExists(_certificateId)
        returns (
            string memory certificateId,
            string memory certificateType,
            string memory holderName,
            string memory institutionName,
            string memory qualificationName,
            string memory imageHash,
            address issuer,
            address currentHolder,
            uint256 issuedAt,
            uint256 expiryDate,
            bool isValid,
            bool isRevoked
        )
    {
        Certificate memory c = certificates[_certificateId];
        return (
            c.certificateId,
            c.certificateType,
            c.holderName,
            c.institutionName,
            c.qualificationName,
            c.imageHash,
            c.issuer,
            c.currentHolder,
            c.issuedAt,
            c.expiryDate,
            c.isValid,
            c.isRevoked
        );
    }

    // Get certificate transfer history
    function getTransferHistory(string memory _certificateId)
        public
        view
        certificateExists(_certificateId)
        returns (Transfer[] memory)
    {
        return certificateTransfers[_certificateId];
    }

    // Get verification logs
    function getVerificationLogs(string memory _certificateId)
        public
        view
        certificateExists(_certificateId)
        returns (VerificationLog[] memory)
    {
        return verificationLogs[_certificateId];
    }

    // Get total number of certificates
    function getTotalCertificates() public view returns (uint256) {
        return certificateIds.length;
    }

    // Get all certificate IDs (paginated)
    function getCertificateIds(uint256 _offset, uint256 _limit)
        public
        view
        returns (string[] memory)
    {
        require(_offset < certificateIds.length, "Offset out of bounds");

        uint256 end = _offset + _limit;
        if (end > certificateIds.length) {
            end = certificateIds.length;
        }

        uint256 resultLength = end - _offset;
        string[] memory result = new string[](resultLength);

        for (uint256 i = 0; i < resultLength; i++) {
            result[i] = certificateIds[_offset + i];
        }

        return result;
    }

    // Check if issuer is authorized
    function isAuthorizedIssuer(address _issuer) public view returns (bool) {
        return authorizedIssuers[_issuer];
    }
}
