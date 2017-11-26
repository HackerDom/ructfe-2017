function getTransactionsByAccount(myaccount, startBlockNumber, endBlockNumber) {
  var acc_log = [];
  for (var i = startBlockNumber; i <= endBlockNumber; i++) {
    var block = eth.getBlock(i, true);
    if (block !== null && block.transactions !== null) {
      block.transactions.forEach( function(e) {
        if (myaccount === "*" || myaccount === e.from || myaccount === e.to) {
            acc_log.push({
                "from": e.from,
                "to": e.to,
                "value": e.value,
                "block": e.blockNumber,
                "input": e.input,
                "transactionIndex": e.transactionIndex
            });
        }
      })
    }
  }
  return acc_log;
}