"""
AI Avatar Platform Main Entry Point
"""
import asyncio
import argparse
from pathlib import Path
from core.platform_manager import PlatformManager
from core.config_manager import ConfigManager
from utils.logger import setup_logger

async def main():
    """Main entry point for the AI Avatar Platform"""
    parser = argparse.ArgumentParser(description="AI Avatar Platform")
    parser.add_argument("--config", default="config/config2.yaml", help="Configuration file path")
    parser.add_argument("--mode", choices=["avatar", "content", "analytics", "full"], 
                       default="full", help="Platform operation mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger("platform", debug=args.debug)
    logger.info("Starting AI Avatar Platform...")
    
    try:
        # Initialize configuration
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        
        # Initialize platform manager
        platform = PlatformManager(config, mode=args.mode)
        
        # Start platform
        await platform.start()
        
        logger.info("Platform started successfully")
        
        # Keep running until interrupted
        try:
            await platform.run()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        finally:
            await platform.stop()
            
    except Exception as e:
        logger.error(f"Platform startup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())