from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from api.deps import get_current_user, get_current_tenant
from models.user import User
from models.tenant import Tenant
from models.agent import AgentType, AgentInstance
from models.interaction import Interaction
from services.agent_orchestrator import AgentFactory

router = APIRouter()


@router.get("/catalog")
async def get_agent_catalog(
    category: Optional[str] = Query(None),
    featured_only: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """Get available agent types in the catalog."""
    query = select(AgentType).where(AgentType.is_active == True)
    
    if category:
        query = query.where(AgentType.category == category)
    
    if featured_only:
        query = query.where(AgentType.is_featured == True)
    
    result = await db.execute(query)
    agent_types = result.scalars().all()
    
    return [
        {
            "id": agent.id,
            "name": agent.name,
            "display_name": agent.display_name,
            "description": agent.description,
            "category": agent.category,
            "base_price_monthly": agent.base_price_monthly,
            "price_per_query": agent.price_per_query,
            "trial_enabled": agent.trial_enabled,
            "supports_file_upload": agent.supports_file_upload,
            "supports_integrations": agent.supports_integrations,
            "is_featured": agent.is_featured
        }
        for agent in agent_types
    ]


@router.post("/trial")
async def start_trial(
    agent_type_id: int,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """Start a trial for an agent type."""
    # Check if tenant can start trials
    if not current_tenant.is_trial_active:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Trial period has expired. Please upgrade your plan."
        )
    
    # Get agent type
    result = await db.execute(select(AgentType).where(AgentType.id == agent_type_id))
    agent_type = result.scalar_one_or_none()
    
    if not agent_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent type not found"
        )
    
    if not agent_type.trial_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trial not available for this agent type"
        )
    
    # Check if trial already exists
    existing_query = select(AgentInstance).where(
        AgentInstance.tenant_id == current_tenant.id,
        AgentInstance.agent_type_id == agent_type_id,
        AgentInstance.status.in_(["provisioning", "active"])
    )
    result = await db.execute(existing_query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trial already active for this agent type"
        )
    
    # Create agent instance
    agent_instance = AgentInstance(
        name=f"{agent_type.display_name} (Trial)",
        tenant_id=current_tenant.id,
        agent_type_id=agent_type.id,
        config=agent_type.config_template.copy(),
        model=agent_type.default_model,
        temperature=agent_type.default_temperature,
        status="provisioning",
        resource_quota={
            "max_queries": 50,  # Trial limit
            "max_storage_mb": 100,
            "timeout_seconds": 30
        }
    )
    
    db.add(agent_instance)
    await db.commit()
    await db.refresh(agent_instance)
    
    # TODO: Trigger async provisioning task
    # provision_agent_instance.delay(agent_instance.id)
    
    return {
        "message": "Trial started successfully",
        "agent_instance_id": agent_instance.id,
        "status": agent_instance.status
    }


@router.get("/instances")
async def get_agent_instances(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """Get tenant's agent instances."""
    query = select(AgentInstance).where(
        AgentInstance.tenant_id == current_tenant.id,
        AgentInstance.status != "deleted"
    )
    
    result = await db.execute(query)
    instances = result.scalars().all()
    
    return [
        {
            "id": instance.id,
            "name": instance.name,
            "agent_type_id": instance.agent_type_id,
            "status": instance.status,
            "queries_count": instance.queries_count,
            "tokens_used": instance.tokens_used,
            "last_used": instance.last_used,
            "provisioned_at": instance.provisioned_at
        }
        for instance in instances
    ]


@router.post("/instances/{instance_id}/query")
async def query_agent(
    instance_id: int,
    prompt: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """Send a query to an agent instance."""
    # Get agent instance
    query = select(AgentInstance).where(
        AgentInstance.id == instance_id,
        AgentInstance.tenant_id == current_tenant.id,
        AgentInstance.status == "active"
    )
    result = await db.execute(query)
    instance = result.scalar_one_or_none()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent instance not found or not active"
        )
    
    # Check trial quota
    if current_tenant.plan == "trial":
        if not current_tenant.is_trial_active:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Trial quota exceeded. Please upgrade your plan."
            )
    
    # TODO: Execute agent query using LangGraph orchestrator
    try:
        # Create agent orchestrator
        agent_config = instance.config.copy()
        agent_config["collection_name"] = instance.qdrant_collection_name
        
        agent = AgentFactory.create_agent(
            agent_type="hr_assistant",  # TODO: Get from instance.agent_type.name
            config=agent_config
        )
        
        # Execute query
        start_time = datetime.utcnow()
        result = await agent.execute(prompt)
        
        # Save interaction
        interaction = Interaction(
            prompt=prompt,
            response=result["response"],
            model=result["metadata"].get("model", instance.model),
            tokens_input=len(prompt.split()),  # Rough estimate
            tokens_output=len(result["response"].split()),  # Rough estimate
            tokens_total=len(prompt.split()) + len(result["response"].split()),
            response_time_ms=result["execution_time_ms"],
            context_chunks=result.get("context_used", 0),
            status="completed" if result["success"] else "failed",
            error_message=result.get("error"),
            tenant_id=current_tenant.id,
            user_id=current_user.id,
            agent_instance_id=instance.id
        )
        
        db.add(interaction)
        
        # Update usage counters
        instance.queries_count += 1
        instance.tokens_used += interaction.tokens_total
        instance.last_used = datetime.utcnow()
        
        if current_tenant.plan == "trial":
            current_tenant.trial_queries_used += 1
        
        await db.commit()
        
        return {
            "response": result["response"],
            "model": interaction.model,
            "tokens_used": interaction.tokens_total,
            "response_time_ms": interaction.response_time_ms,
            "context_chunks": interaction.context_chunks,
            "interaction_id": interaction.id
        }
        
    except Exception as e:
        # Log error and return generic response
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error executing agent query: {e}")
        
        response = f"I apologize, but I encountered an error processing your request: {str(e)}"
    
        
        # Update usage counters (even for errors)
        instance.queries_count += 1
        current_tenant.trial_queries_used += 1
        
        await db.commit()
        
        return {
            "response": response,
            "model": instance.model,
            "tokens_used": 0,
            "response_time_ms": 0,
            "error": True
        }
