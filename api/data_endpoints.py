"""
AutoPPM Data API Endpoints
API endpoints for data ingestion and market data retrieval
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from loguru import logger

from database.connection import get_database_session
from models.market_data import (
    MarketDataResponse, HistoricalDataRequest, HistoricalDataResponse,
    InstrumentResponse, PortfolioSnapshotResponse
)
from services.data_ingestion_service import get_data_ingestion_service
from services.zerodha_service import get_zerodha_service

router = APIRouter(prefix="/api/data", tags=["Data"])


@router.get("/market-data/{symbol}", response_model=MarketDataResponse)
async def get_market_data(
    symbol: str,
    db: Session = Depends(get_database_session)
):
    """Get current market data for a symbol"""
    try:
        # Get latest market data from database
        from models.market_data import MarketData
        
        latest_data = db.query(MarketData).filter(
            MarketData.symbol == symbol.upper()
        ).order_by(MarketData.timestamp.desc()).first()
        
        if not latest_data:
            raise HTTPException(status_code=404, detail=f"Market data not found for {symbol}")
        
        return MarketDataResponse(
            symbol=latest_data.symbol,
            last_price=latest_data.last_price,
            change=latest_data.change,
            change_percent=latest_data.change_percent,
            volume=latest_data.volume,
            timestamp=latest_data.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/market-data", response_model=List[MarketDataResponse])
async def get_market_data_batch(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    db: Session = Depends(get_database_session)
):
    """Get market data for multiple symbols"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        
        from models.market_data import MarketData
        
        # Get latest data for each symbol
        market_data = []
        for symbol in symbol_list:
            latest = db.query(MarketData).filter(
                MarketData.symbol == symbol
            ).order_by(MarketData.timestamp.desc()).first()
            
            if latest:
                market_data.append(MarketDataResponse(
                    symbol=latest.symbol,
                    last_price=latest.last_price,
                    change=latest.change,
                    change_percent=latest.change_percent,
                    volume=latest.volume,
                    timestamp=latest.timestamp
                ))
        
        return market_data
        
    except Exception as e:
        logger.error(f"Failed to get batch market data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/historical-data", response_model=HistoricalDataResponse)
async def get_historical_data(
    request: HistoricalDataRequest,
    db: Session = Depends(get_database_session)
):
    """Get historical market data for a symbol"""
    try:
        from models.market_data import MarketData
        
        # Get historical data from database
        data = db.query(MarketData).filter(
            MarketData.symbol == request.symbol.upper(),
            MarketData.timestamp >= request.from_date,
            MarketData.timestamp <= request.to_date
        ).order_by(MarketData.timestamp.asc()).all()
        
        if not data:
            raise HTTPException(
                status_code=404, 
                detail=f"Historical data not found for {request.symbol}"
            )
        
        # Format data for response
        formatted_data = [
            {
                "timestamp": record.timestamp,
                "open": record.open_price,
                "high": record.high_price,
                "low": record.low_price,
                "close": record.close_price,
                "volume": record.volume,
                "change": record.change,
                "change_percent": record.change_percent
            }
            for record in data
        ]
        
        return HistoricalDataResponse(
            symbol=request.symbol,
            data=formatted_data,
            interval=request.interval,
            from_date=request.from_date,
            to_date=request.to_date
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get historical data for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/instruments", response_model=List[InstrumentResponse])
async def get_instruments(
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    instrument_type: Optional[str] = Query(None, description="Filter by instrument type"),
    db: Session = Depends(get_database_session)
):
    """Get list of instruments"""
    try:
        from models.market_data import Instrument
        
        query = db.query(Instrument).filter(Instrument.is_active == "Y")
        
        if exchange:
            query = query.filter(Instrument.exchange == exchange.upper())
        
        if instrument_type:
            query = query.filter(Instrument.instrument_type == instrument_type.upper())
        
        instruments = query.limit(100).all()
        
        return [
            InstrumentResponse(
                instrument_token=inst.instrument_token,
                trading_symbol=inst.trading_symbol,
                name=inst.name,
                exchange=inst.exchange,
                instrument_type=inst.instrument_type,
                lot_size=inst.lot_size,
                tick_size=inst.tick_size
            )
            for inst in instruments
        ]
        
    except Exception as e:
        logger.error(f"Failed to get instruments: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/portfolio/{user_id}", response_model=PortfolioSnapshotResponse)
async def get_portfolio_snapshot(
    user_id: int,
    db: Session = Depends(get_database_session)
):
    """Get latest portfolio snapshot for a user"""
    try:
        from models.market_data import PortfolioSnapshot
        
        snapshot = db.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.user_id == user_id
        ).order_by(PortfolioSnapshot.snapshot_time.desc()).first()
        
        if not snapshot:
            raise HTTPException(
                status_code=404, 
                detail=f"Portfolio snapshot not found for user {user_id}"
            )
        
        return PortfolioSnapshotResponse(
            user_id=snapshot.user_id,
            total_value=snapshot.total_value,
            total_pnl=snapshot.total_pnl,
            day_pnl=snapshot.day_pnl,
            total_holdings=snapshot.total_holdings,
            snapshot_time=snapshot.snapshot_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get portfolio snapshot for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/ingestion/start")
async def start_data_ingestion():
    """Start data ingestion service"""
    try:
        service = get_data_ingestion_service()
        await service.start_ingestion()
        
        return {"message": "Data ingestion service started successfully"}
        
    except Exception as e:
        logger.error(f"Failed to start data ingestion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/ingestion/stop")
async def stop_data_ingestion():
    """Stop data ingestion service"""
    try:
        service = get_data_ingestion_service()
        await service.stop_ingestion()
        
        return {"message": "Data ingestion service stopped successfully"}
        
    except Exception as e:
        logger.error(f"Failed to stop data ingestion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ingestion/status")
async def get_ingestion_status():
    """Get data ingestion service status"""
    try:
        service = get_data_ingestion_service()
        
        return {
            "is_running": service.is_running,
            "ingestion_interval": service.ingestion_interval,
            "last_sync": service.last_sync
        }
        
    except Exception as e:
        logger.error(f"Failed to get ingestion status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sync/portfolio")
async def sync_portfolio_data():
    """Manually trigger portfolio synchronization"""
    try:
        service = get_data_ingestion_service()
        await service.sync_portfolio_data()
        
        return {"message": "Portfolio synchronization completed successfully"}
        
    except Exception as e:
        logger.error(f"Failed to sync portfolio data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sync/instruments")
async def sync_instruments():
    """Manually trigger instrument synchronization"""
    try:
        service = get_data_ingestion_service()
        await service.sync_instruments()
        
        return {"message": "Instrument synchronization completed successfully"}
        
    except Exception as e:
        logger.error(f"Failed to sync instruments: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_database_session)):
    """Get dashboard summary data"""
    try:
        from models.market_data import MarketData, Instrument, PortfolioSnapshot
        
        # Get counts
        total_instruments = db.query(Instrument).filter(Instrument.is_active == "Y").count()
        total_market_records = db.query(MarketData).count()
        total_portfolio_snapshots = db.query(PortfolioSnapshot).count()
        
        # Get latest market data count
        today = datetime.utcnow().date()
        today_market_records = db.query(MarketData).filter(
            MarketData.timestamp >= today
        ).count()
        
        return {
            "total_instruments": total_instruments,
            "total_market_records": total_market_records,
            "total_portfolio_snapshots": total_portfolio_snapshots,
            "today_market_records": today_market_records,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
