// PLANTILLA POR DEFECTO
// import { StatusBar } from 'expo-status-bar';
// import { StyleSheet, Text, View } from 'react-native';

// export default function App() {
//   return (
//     <View style={styles.container}>
//       <Text>Open up App.js to start working on your app!app</Text>
//       <StatusBar style="auto" />
//     </View>
//   );
// }

// const styles = StyleSheet.create({
//   container: {
//     flex: 1,
//     backgroundColor: '#fff',
//     alignItems: 'center',
//     justifyContent: 'center',
//   },
// });

import 'react-native-gesture-handler';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

// IMPORTACIÓN VISTAS
import LoginVista from './src/vistas/LoginVista';
import RegistroVista from './src/vistas/RegistroVista';
import PrincipalVista from './src/vistas/PrincipalVista';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator 
        initialRouteName="Login"
        screenOptions={{
          headerStyle: { backgroundColor: '#4f46e5' },
          headerTintColor: '#fff',
        }}
      >
        <Stack.Screen 
          name="Login" 
          component={LoginVista} 
          options={{ headerShown: false }} 
        />
        <Stack.Screen 
          name="Registro" 
          component={RegistroVista} 
          options={{ title: 'Crear cuenta' }}
        />
        <Stack.Screen 
          name="Main" 
          component={PrincipalVista} 
          options={{ title: 'GYM EX', headerLeft: null }} // headerLeft: null oculta el botón atrás tras loguear
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}