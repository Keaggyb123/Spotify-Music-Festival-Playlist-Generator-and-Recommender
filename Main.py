import access
import spotipy
import pandas as pd
import ast
from datetime import datetime, timezone
from collections import defaultdict

class SaveSongs:
    def __init__(self):
        # authentication
        self.spotify_token = access.getAccessToken()
        self.sp = spotipy.Spotify(auth=self.spotify_token)
        self.user_id = 'YOUR_USER_ID'
        self.tracks = []
        self.new_playlist_id = ""
        self.artistsDF = None
        self.potentalArtist = []

    def getUserArtist(self):
        print("Creating a User's Favorite Artists DataFrame")
        loopthru = [[5,0],[5,5],[15,10],[25,25],[50,49],[10,0],[50,10],[50,49]]
        scores = [5,4,3,2,1,3,2,1]
        name = []
        uri = []
        genres = []
        followers = []
        popularity = []
        favScore = []
        for i in range(len(loopthru)):
            limit = loopthru[i][0]
            offset = loopthru[i][1]
            if i>4:
                artists = self.sp.current_user_top_artists(limit = limit,time_range='short_term',offset= offset)['items']
                artists += self.sp.current_user_top_artists(limit = limit,time_range='long_term',offset= offset)['items'] 
            else:
                artists = self.sp.current_user_top_artists(limit = limit,offset = offset)['items']
            for artist in artists:
                name.append(artist['name'])
                uri.append(artist['uri'])
                genres.append(artist['genres'])
                followers.append(artist['followers']['total'])
                popularity.append(artist['popularity'])
                favScore.append(scores[i])
        top50uri = uri[:50]
        for i in top50uri:
            artists = self.sp.artist_related_artists(i)['artists']
            for artist in artists:
                name.append(artist['name'])
                uri.append(artist['uri'])
                genres.append(artist['genres'])
                followers.append(artist['followers']['total'])
                popularity.append(artist['popularity'])
                favScore.append(1)
        dic = {'Name':name,'uri':uri,'Genre':genres,'Followers':followers,'Popularity':popularity,'FavScore':favScore}
        art = pd.DataFrame(data = dic)
        art['FavScore'] = art.groupby('Name')['FavScore'].transform('sum')
        self.artistsDF = art.drop_duplicates(subset =['Name']).reset_index(drop = True)

    def recommend(self,start_range = None, end_range = None, city = None, state = None):
        if self.artistsDF is None:
            self.getUserArtist()
        df = pd.read_excel('FestivalDB/Festival_Characteristics.xlsx')
        df['artists'] = df['artists'].apply(ast.literal_eval)
        df['startDate'] = pd.to_datetime(df['startDate'])
        df['endDate'] = pd.to_datetime(df['endDate'])
        df['state'] = df['state'].str[1:]

        fests = df.copy()

        # filers
        if start_range:
            fests = fests[fests['startDate'] > start_range]
        if end_range:
            fests = fests[fests['endDate'] < end_range]
            
        if city:
            fests = fests[fests['city'] == city]

        elif state:
            fests = fests[fests['state'] == state]
        dic = fests.set_index('name')['artists'].to_dict()

        score = defaultdict(int)
        for festival in list(dic.keys()):
            lineup = dic[festival]
            for artist in lineup:
                if artist in self.artistsDF['Name'].to_list():
                    score[festival] += self.artistsDF[self.artistsDF['Name'] == artist]['FavScore'].iloc[0]
            score[festival] += 0

        final = pd.DataFrame(score.items(),columns =['Festival','Score']).sort_values('Score',ascending=False)
        top5 = final['Festival'].iloc[:5].to_list()
        print('We Recommed:')
        a = 1
        for i in top5:
            print(str(a) + ". " + i)
            a +=1
        
    def create_playlist(self,festivalName = None):
        assert type(festivalName) == str, "Festival Name is needed"
        if self.artistsDF is None:
            self.getUserArtist()
        df = pd.read_excel('FestivalDB/Festival_Characteristics.xlsx')
        lineup = ast.literal_eval(df[df['name'] == festivalName]['artists'].iloc[0])
        scores = []
        for artist in lineup:
            # search for the artist in spotify
            search = self.sp.search(q='artist:' + artist, type='artist')['artists']['items']
            if search == []: #checking if seacrh works - add regex or address edge case
                continue
            first_value = search[0] # number 1 search result
            if first_value['uri'] in self.artistsDF.uri.to_list():
                score = self.artistsDF[self.artistsDF.uri==first_value['uri']]['FavScore'].iloc[0]
                self.potentalArtist.append(first_value['uri'])
                scores.append(score)
        s = sum(scores)
        result = [round(value*93/s) for value in scores]
        
        for i in range(len(self.potentalArtist)):
            ttp = self.sp.artist_top_tracks(self.potentalArtist[i])['tracks'][:result[i]]
            for song in ttp:
                self.tracks.append(song['uri'])
        
        # Create a new playlist
        print("Trying to create playlist...")
        today = datetime.now(timezone.utc).date()
        today_string = today.strftime("%m-%d-%Y")
        playlist = self.sp.user_playlist_create(self.user_id,festivalName + ' ' + today_string)
        self.new_playlist_id = playlist['uri']
        print('Adding Tracks')
        self.sp.playlist_add_items(playlist_id = playlist['uri'], items = self.tracks[:99])
        print('Your already Dead')


