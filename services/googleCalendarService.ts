import { GOOGLE_CLIENT_ID, GOOGLE_API_SCOPES } from '../constants';

declare global {
  interface Window {
    google: any;
    gapi: any;
  }
}

export interface GoogleUser {
  email: string;
  name: string;
  accessToken: string;
}

let tokenClient: any = null;
let gapiInitialized = false;
let gisInitialized = false;

const GAPI_SCRIPT_ID = 'gapi-script';
const GIS_SCRIPT_ID = 'gis-script'; // Already in index.html, but good to have a ref

/**
 * Initializes the Google API client library (gapi) for Calendar API calls.
 */
const initializeGapiClient = async (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (document.getElementById(GAPI_SCRIPT_ID)) {
       // If gapi is already loaded or being loaded by this script, wait for it.
      const checkGapi = () => {
        if (window.gapi && window.gapi.client) {
          gapiInitialized = true;
          resolve();
        } else {
          setTimeout(checkGapi, 100);
        }
      };
      checkGapi();
      return;
    }

    const script = document.createElement('script');
    script.id = GAPI_SCRIPT_ID;
    script.src = 'https://apis.google.com/js/api.js';
    script.async = true;
    script.defer = true;
    script.onload = () => {
      window.gapi.load('client', async () => {
        try {
          await window.gapi.client.init({}); // Minimal init, discoveryDocs loaded per call
          gapiInitialized = true;
          resolve();
        } catch (error) {
          console.error('Error initializing GAPI client:', error);
          reject(error);
        }
      });
    };
    script.onerror = (error) => {
      console.error('Error loading GAPI script:', error);
      reject(error);
    };
    document.body.appendChild(script);
  });
};


/**
 * Initializes the Google Identity Services (GIS) token client.
 */
export const initializeTokenClient = (
  callback: (tokenResponse: any) => void,
  errorCallback: (error: any) => void
): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (!GOOGLE_CLIENT_ID || GOOGLE_CLIENT_ID === 'YOUR_GOOGLE_CLIENT_ID_HERE') {
      const errorMsg = "Google Client ID is not configured. Please set it in constants.ts.";
      console.error(errorMsg);
      errorCallback({ error: errorMsg });
      reject(new Error(errorMsg));
      return;
    }

    const checkGis = () => {
      if (window.google && window.google.accounts && window.google.accounts.oauth2) {
        if (tokenClient) { // Already initialized
            gisInitialized = true;
            resolve();
            return;
        }
        try {
          tokenClient = window.google.accounts.oauth2.initTokenClient({
            client_id: GOOGLE_CLIENT_ID,
            scope: GOOGLE_API_SCOPES,
            callback: (tokenResponse: any) => {
              if (tokenResponse && tokenResponse.access_token) {
                callback(tokenResponse);
              } else if (tokenResponse && tokenResponse.error) {
                console.error('Token client error response:', tokenResponse);
                errorCallback(tokenResponse);
              } else {
                 console.warn('Token client response without access_token or error:', tokenResponse);
                 // It could be an intermediate response, or user closed popup.
                 // errorCallback might be too strong if user just closed popup.
                 // For now, let's call errorCallback if no access token.
                 errorCallback({error: "Authorization failed or popup closed."});
              }
            },
            error_callback: (error: any) => { // Handle explicit errors from initTokenClient or token request
              console.error('GIS Token Client Error:', error);
              errorCallback(error);
            }
          });
          gisInitialized = true;
          resolve();
        } catch (initError) {
          console.error("Error initializing GIS token client:", initError);
          errorCallback(initError);
          reject(initError);
        }
      } else {
        setTimeout(checkGis, 100); // Wait for GIS to load
      }
    };
    checkGis();
    // Also ensure GAPI client is ready for API calls
    initializeGapiClient().catch(gapiError => {
        console.error("Failed to initialize GAPI for calendar service:", gapiError);
        // This might not need to reject initializeTokenClient, but it's a dependency for calendar calls
    });
  });
};

/**
 * Initiates the Google Sign-In flow.
 */
export const requestGoogleAccessToken = (): void => {
  if (tokenClient) {
    // Prompt the user to select an account and grant access if they haven't yet.
    tokenClient.requestAccessToken({ prompt: '' }); // Use 'consent' to force consent screen if needed for re-auth. '' is often fine.
  } else {
    console.error('Google Token Client not initialized. Cannot request access token.');
    // Potentially trigger an error message to the user or an error callback.
    throw new Error('Google Token Client not initialized.');
  }
};

/**
 * Revokes the Google access token (signs the user out of the app's calendar access).
 */
export const revokeGoogleAccessToken = (accessToken: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (!accessToken) {
      resolve(); // No token to revoke
      return;
    }
    window.google.accounts.oauth2.revoke(accessToken, () => {
      console.log('Google access token revoked.');
      resolve();
    });
    // Note: Revoke doesn't have an explicit error callback in this simple form.
    // For production, handle potential network errors if this were a fetch call.
  });
};


/**
 * Fetches user's profile information using the access token.
 */
export const getGoogleUserProfile = async (accessToken: string): Promise<{ email: string; name: string } | null> => {
  if (!gapiInitialized || !window.gapi.client) {
    await initializeGapiClient(); // Ensure GAPI is loaded
  }
  try {
    // Set the access token for GAPI client
    window.gapi.client.setToken({ access_token: accessToken });
    // Load People API if not already loaded (though not strictly necessary for basic email)
    // The userinfo endpoint is simpler
    const response = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
    if (!response.ok) {
      console.error('Failed to fetch user profile:', response);
      throw new Error(`Failed to fetch user profile: ${response.statusText}`);
    }
    const profile = await response.json();
    return { email: profile.email, name: profile.name || profile.given_name || '' };
  } catch (error) {
    console.error('Error fetching Google user profile:', error);
    return null;
  } finally {
    if (window.gapi && window.gapi.client) {
      window.gapi.client.setToken(null); // Clear token after use
    }
  }
};


/**
 * Lists upcoming events from the user's primary Google Calendar.
 * @param accessToken The Google access token.
 * @param timeMin ISO string for start time.
 * @param timeMax ISO string for end time.
 */
export const listCalendarEvents = async (
  accessToken: string,
  timeMin: string,
  timeMax: string
): Promise<any[]> => {
  if (!gapiInitialized || !window.gapi.client) {
    await initializeGapiClient(); // Ensure GAPI is loaded
  }
  try {
    window.gapi.client.setToken({ access_token: accessToken });
    await window.gapi.client.load('calendar', 'v3');
    
    const response = await window.gapi.client.calendar.events.list({
      calendarId: 'primary',
      timeMin: timeMin,
      timeMax: timeMax,
      showDeleted: false,
      singleEvents: true,
      orderBy: 'startTime',
    });
    return response.result.items || [];
  } catch (error) {
    console.error('Error listing calendar events:', error);
    throw error; // Re-throw to be handled by the caller
  } finally {
     if (window.gapi && window.gapi.client) {
      window.gapi.client.setToken(null); // Clear token
    }
  }
};

/**
 * Creates an event on the user's primary Google Calendar.
 * @param accessToken The Google access token.
 * @param eventDetails Object containing summary, start.dateTime, end.dateTime, etc.
 *  Example: { summary: 'Meeting', start: { dateTime: '2024-08-01T10:00:00-07:00', timeZone: 'America/Los_Angeles' }, end: { dateTime: '2024-08-01T11:00:00-07:00', timeZone: 'America/Los_Angeles' } }
 */
export const createCalendarEvent = async (
  accessToken: string,
  eventDetails: { summary: string; description?: string; start: { dateTime: string; timeZone: string }; end: { dateTime: string; timeZone: string }; attendees?: {email: string}[] }
): Promise<any> => {
   if (!gapiInitialized || !window.gapi.client) {
    await initializeGapiClient(); // Ensure GAPI is loaded
  }
  try {
    window.gapi.client.setToken({ access_token: accessToken });
    await window.gapi.client.load('calendar', 'v3');

    const response = await window.gapi.client.calendar.events.insert({
      calendarId: 'primary',
      resource: eventDetails,
    });
    return response.result;
  } catch (error) {
    console.error('Error creating calendar event:', error);
    throw error; // Re-throw to be handled by the caller
  } finally {
     if (window.gapi && window.gapi.client) {
      window.gapi.client.setToken(null); // Clear token
    }
  }
};
