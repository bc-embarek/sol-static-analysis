pragma solidity ^0.8.0;

contract ContractBalanceTest {
    function test() internal {
        payable(msg.sender).transfer(address(this).balance);
    }

    function test2() external {
        test();
    }
}
