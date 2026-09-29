const CertificateAuthentication = artifacts.require("CertificateAuthentication");

module.exports = function(deployer) {
  deployer.deploy(CertificateAuthentication);
};
