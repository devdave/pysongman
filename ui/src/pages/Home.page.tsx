import { Text } from '@mantine/core'
import { useAppContext } from '@src/contexts/App.context';

export function HomePage() {
    const { api } = useAppContext()

    api.songs.list(1, 100).then((response) => {
        console.log(response)
    })

  return (
    <>
      <Text>PySongMan</Text>
    </>
  );
}
