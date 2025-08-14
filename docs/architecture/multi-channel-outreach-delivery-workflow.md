# Multi-Channel Outreach Delivery Workflow

## Outreach Delivery Sequence Diagram

```mermaid
sequenceDiagram
    participant ORCH as Agent Orchestrator
    participant OUT as Outreach Agent
    participant DB as Supabase Database
    participant BRAVO as Bravo Email Service
    participant TEXTBEE as TextBee API (SMS/WhatsApp)
    participant WH as Webhook Handler
    participant RT as Realtime Engine
    participant UI as Frontend UI

    Note over ORCH,UI: Outreach Campaign Creation Phase
    
    ORCH->>OUT: generate_campaigns(businesses, demo_urls)
    OUT->>OpenAI: Generate personalized messages
    OpenAI->>OUT: Return email/SMS/WhatsApp content
    OUT->>DB: Store outreach_campaigns with delivery_status = pending
    OUT->>ORCH: Campaigns ready for delivery
    
    Note over ORCH,UI: Multi-Channel Message Delivery Phase
    
    par Email Delivery
        OUT->>BRAVO: POST /send {recipient, subject, body, webhook_url, metadata}
        BRAVO->>OUT: {message_id, status: 'queued'}
        OUT->>DB: Update delivery_status.email_sent = true, provider_id
        
        Note over BRAVO: Email Processing (async)
        BRAVO->>BRAVO: Process and send email
        BRAVO->>WH: POST /webhooks/email-delivery {message_id, event: 'sent'}
        WH->>DB: Update delivery_status.email_delivered = true
        DB->>RT: Trigger delivery update event
        RT->>UI: Real-time delivery notification
        
        Note over BRAVO: Email Engagement Tracking (async)
        loop Email Tracking Events
            BRAVO->>WH: POST /webhooks/email-delivery {event: 'opened'|'clicked'}
            WH->>DB: Update delivery_status with engagement data
            DB->>RT: Trigger engagement event
            RT->>UI: Real-time engagement update
        end
        
    and WhatsApp Delivery
        OUT->>TEXTBEE: POST /v1/whatsapp/send {recipient, message, webhook_url, metadata}
        TEXTBEE->>OUT: {message_id, status: 'queued'}
        OUT->>DB: Update delivery_status.whatsapp_sent = true, provider_id
        
        Note over TEXTBEE: WhatsApp Processing (async)
        TEXTBEE->>TEXTBEE: Process and send WhatsApp message
        TEXTBEE->>WH: POST /webhooks/sms-whatsapp-delivery {message_id, status: 'delivered'}
        WH->>DB: Update delivery_status.whatsapp_delivered = true
        DB->>RT: Trigger delivery update event
        RT->>UI: Real-time delivery notification
        
        Note over TEXTBEE: WhatsApp Read Receipts (async)
        TEXTBEE->>WH: POST /webhooks/sms-whatsapp-delivery {status: 'read'}
        WH->>DB: Update delivery_status.whatsapp_read = true
        DB->>RT: Trigger read receipt event
        RT->>UI: Real-time read confirmation
        
    and SMS Delivery
        OUT->>TEXTBEE: POST /v1/sms/send {recipient, message, webhook_url, metadata}
        TEXTBEE->>OUT: {message_id, status: 'queued'}
        OUT->>DB: Update delivery_status.sms_sent = true, provider_id
        
        Note over TEXTBEE: SMS Processing (async)
        TEXTBEE->>TEXTBEE: Process and send SMS
        TEXTBEE->>WH: POST /webhooks/sms-whatsapp-delivery {message_id, status: 'delivered'}
        WH->>DB: Update delivery_status.sms_delivered = true
        DB->>RT: Trigger delivery update event
        RT->>UI: Real-time delivery notification
    end
    
    Note over ORCH,UI: Error Handling and Retry Logic
    
    alt Delivery Failure
        BRAVO-->>WH: POST /webhooks/email-delivery {event: 'bounced', reason}
        WH->>DB: Update delivery_status.email_bounced = true, error_message
        WH->>OUT: Trigger retry logic if retryable
        
        alt Retryable Error
            OUT->>OUT: Wait exponential backoff delay
            OUT->>BRAVO: Retry with alternative email or modified content
        else Permanent Failure
            OUT->>DB: Mark delivery_status.email_status = 'failed'
            DB->>RT: Trigger failure notification
            RT->>UI: Display delivery failure with reason
        end
    end
    
    Note over ORCH,UI: Delivery Reporting and Analytics
    
    WH->>WH: Aggregate delivery metrics every 5 minutes
    WH->>DB: Update campaign performance statistics
    DB->>RT: Trigger metrics update event
    RT->>UI: Real-time delivery dashboard updates
```

## Delivery Status State Machine

```mermaid
stateDiagram-v2
    [*] --> Pending: Campaign created
    
    state "Email Channel" as EmailChannel {
        Pending --> EmailQueued: Send request submitted
        EmailQueued --> EmailSent: Provider confirms sending
        EmailSent --> EmailDelivered: Delivery confirmation
        EmailDelivered --> EmailOpened: Recipient opens email
        EmailOpened --> EmailClicked: Recipient clicks link
        
        EmailQueued --> EmailFailed: Send failure
        EmailSent --> EmailBounced: Delivery bounce
        EmailFailed --> EmailRetrying: Retry logic triggered
        EmailRetrying --> EmailQueued: Retry attempt
        EmailRetrying --> EmailPermanentFailed: Max retries exceeded
    }
    
    state "WhatsApp Channel" as WhatsAppChannel {
        Pending --> WhatsAppQueued: Send request submitted
        WhatsAppQueued --> WhatsAppSent: Provider confirms sending
        WhatsAppSent --> WhatsAppDelivered: Delivery confirmation
        WhatsAppDelivered --> WhatsAppRead: Recipient reads message
        WhatsAppRead --> WhatsAppReplied: Recipient replies
        
        WhatsAppQueued --> WhatsAppFailed: Send failure
        WhatsAppSent --> WhatsAppUndelivered: Delivery failure
        WhatsAppFailed --> WhatsAppRetrying: Retry logic triggered
        WhatsAppRetrying --> WhatsAppQueued: Retry attempt
        WhatsAppRetrying --> WhatsAppPermanentFailed: Max retries exceeded
    }
    
    state "SMS Channel" as SMSChannel {
        Pending --> SMSQueued: Send request submitted
        SMSQueued --> SMSSent: Provider confirms sending
        SMSSent --> SMSDelivered: Delivery confirmation
        
        SMSQueued --> SMSFailed: Send failure
        SMSSent --> SMSUndelivered: Delivery failure
        SMSFailed --> SMSRetrying: Retry logic triggered
        SMSRetrying --> SMSQueued: Retry attempt
        SMSRetrying --> SMSPermanentFailed: Max retries exceeded
    }
```

## Webhook Processing Architecture

**Webhook Handler Service:**
```python
class WebhookHandler:
    async def process_email_webhook(self, payload: BravoWebhookPayload):
        """Process Bravo email delivery webhooks"""
        try:
            # Validate webhook signature
            self._verify_bravo_signature(payload)
            
            # Extract campaign context
            business_id = payload.campaign_metadata['business_id']
            campaign_id = payload.campaign_metadata['outreach_campaign_id']
            
            # Update delivery status in database
            await self.outreach_repo.update_delivery_status(
                campaign_id=campaign_id,
                channel='email',
                status_update={
                    f'email_{payload.event_type}': True,
                    f'email_{payload.event_type}_at': payload.timestamp,
                    'email_provider_id': payload.message_id,
                    'email_callback_data': payload.dict()
                }
            )
            
            # Trigger real-time notification
            await self.realtime_service.broadcast_delivery_update({
                'type': 'delivery_update',
                'business_id': business_id,
                'campaign_id': campaign_id,
                'channel': 'email',
                'status': payload.event_type,
                'timestamp': payload.timestamp
            })
            
            # Handle bounce/failure scenarios
            if payload.event_type in ['bounced', 'failed']:
                await self._handle_delivery_failure(
                    campaign_id, 'email', payload.bounce_reason or 'Unknown error'
                )
                
        except WebhookValidationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
            
    async def process_textbee_webhook(self, payload: TextBeeWebhookPayload):
        """Process TextBee SMS/WhatsApp delivery webhooks"""
        # Similar implementation for SMS/WhatsApp delivery tracking
        pass
        
    async def _handle_delivery_failure(self, campaign_id: str, channel: str, error_reason: str):
        """Handle delivery failures with retry logic"""
        campaign = await self.outreach_repo.get_by_id(campaign_id)
        
        if self._is_retryable_error(error_reason) and campaign.retry_count < MAX_RETRIES:
            # Schedule retry with exponential backoff
            retry_delay = 2 ** campaign.retry_count * 60  # minutes
            await self.task_queue.schedule_retry(
                task_id=f"retry_delivery_{campaign_id}_{channel}",
                delay=retry_delay,
                payload={'campaign_id': campaign_id, 'channel': channel}
            )
        else:
            # Mark as permanently failed
            await self.outreach_repo.update_delivery_status(
                campaign_id=campaign_id,
                channel=channel,
                status_update={f'{channel}_status': 'permanent_failed'}
            )
```

---
