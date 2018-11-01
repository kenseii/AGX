// AGX ICO

pragma solidity ^0.4.11;

contract agx_ico{
    
    //introducing max agx for sale 
    uint public max_agx = 100000;
    
    //USD to agx
    uint public usd_to_agx = 1000;
    
    //Total number of coins sold to investors
    
    uint public total_agx_sold = 0;
    
    // Mapping the user address to its equity in agx and usd
    
    mapping(address => uint) equity_agx;
    mapping(address => uint) equity_usd;
    
    // Checking if there is agx remaining before selling
    modifier can_buy_agx(uint usd_invested){
        require (usd_invested * usd_to_agx + total_agx_sold <= max_agx);
        _;
    }
    //Getting the equity in agx for an investor and assigning it to the public key address
    function equity_in_agx(address investor) external constant returns(uint){
        return equity_agx[investor];
    }
    
    //Getting the equity in usd for an in investor and assigning it to his key address
    function equity_in_usd(address investor) external constant returns(uint){
        return equity_usd[investor];
    }
    
    //Method to buy agx from usd, before buying we call the can_buy_agx modifier to validate the balance
    function buy_agx(address investor,uint usd_invested) external
    can_buy_agx(usd_invested){
        uint agx_bought = usd_invested * usd_to_agx;
        equity_agx[investor] += agx_bought;
        equity_usd[investor] = equity_agx[investor]/1000;
        total_agx_sold+=agx_bought;
        
    }
    
    //Method to sell agx back to me
    function sell_agx(address investor, uint agx_to_sale) external{
        equity_agx[investor] -= agx_to_sale;
        equity_usd[investor] = equity_agx[investor]/1000;
        total_agx_sold-=agx_to_sale;
    }
    
}

