pragma solidity ^0.4.15;

contract Bank{
  mapping(address=>uint) userBalances;
  uint public totalBankBalance;

  function Bank(){
    totalBankBalance = 0;
  }

  function () payable {
  }

  function getUserBalance(address user) constant returns(uint) {
    return userBalances[user];
  }

  function addToBalance() payable {
    userBalances[msg.sender] += msg.value;
    totalBankBalance += msg.value;
  }

  function withdrawBalance() {
    var amountToWithdraw = userBalances[msg.sender];
    if(amountToWithdraw == 0)
      return;
    require(msg.sender.call.value(amountToWithdraw)());
    totalBankBalance -= userBalances[msg.sender];
	userBalances[msg.sender] = 0;
  }
}
